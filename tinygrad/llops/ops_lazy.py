from __future__ import annotations
from typing import Union, NamedTuple, List, Any, Tuple
from tinygrad.shapetracker import ShapeTracker

from tinygrad.ops import ReduceOps, BinaryOps, MovementOps, ProcessingOps, LoadOps, log_op
Op = Union[BinaryOps, ReduceOps, MovementOps, ProcessingOps, LoadOps]

SHUFFLE_MOVEMENT_OPS = True
MERGE_ELEMENTWISE_OPS = False

class LazyOp(NamedTuple):
  op: Op
  src: List[Union[LazyOp, LazyBuffer]]
  arg: Any = None

class LazyBuffer:
  def __init__(self, shape:tuple, optype:Op, op:LazyOp):
    self.st = ShapeTracker(shape)
    self.optype, self.op = optype, op
    self.realized = None

  @property
  def shape(self): return self.st.shape

  def realize(self:LazyBuffer):
    if self.realized is None:
      srcs = [x.realize() for x in self.op.src]
      self.realized = _realize(self, srcs)
      # in lazy mode, we don't log until we realize
      log_op(self.optype, self.op.op, self.realized, srcs)
    return self.realized

  @staticmethod
  def fromCPU(x):
    return LazyBuffer(x.shape, LoadOps, LazyOp(LoadOps.FROMCPU, [], x))

  def toCPU(self):
    return self.realize().toCPU()

# this function determines the backing buffer
import tinygrad.llops.ops_gpu as gops
def _realize(self:LazyBuffer, srcs:List[gops.GPUBuffer]) -> gops.GPUBuffer:
  if self.optype == LoadOps:
    return gops.GPUBuffer(self.shape, self.op.arg)
  elif self.optype == ReduceOps:
    return gops.reduce_op(self.op.op, srcs[0], self.op.arg)
  elif self.optype == MovementOps:
    return gops.GPUBuffer(self.st, srcs[0])
  elif self.optype == BinaryOps:
    return gops.elementwise_op(list(zip(["A", "B"], srcs)), gops.code_for_op[self.op.op])
  elif self.optype == ProcessingOps:
    return gops.processing_op(self.op.op, srcs[0], srcs[1], self.op.arg)

def elementwise_op(op, srcs:Tuple[LazyBuffer]) -> LazyBuffer:
  out_shape = srcs[0].shape

  if MERGE_ELEMENTWISE_OPS:
    # remove the buffers from any BinaryOps that feed into this
    srcs = [x.op if x.optype == BinaryOps else x for x in srcs]

  return LazyBuffer(out_shape, BinaryOps, LazyOp(op, list(srcs)))

def unary_op(op, x):
  return elementwise_op(op, (x,))

def binary_op(op, x, y):
  return elementwise_op(op, (x,y))

def movement_op(op, x, arg):
  if SHUFFLE_MOVEMENT_OPS and x.optype == BinaryOps:
    # if this MovementOp is being applied to a BinaryOp, apply the MovementOp to all the BinaryOp inputs instead
    def replace_w_movement_op(y:Union[LazyOp, LazyBuffer]) -> LazyBuffer:
      if isinstance(y, LazyBuffer): return movement_op(op, y, arg)
      elif isinstance(y, LazyOp): return elementwise_op(y.op, tuple([replace_w_movement_op(z) for z in y.src]))
    return replace_w_movement_op(x.op)

  ret = LazyBuffer(x.st, MovementOps, LazyOp(op, [x], arg))
  ret.st.movement_op(op, arg)
  return ret

def reduce_op(op, x, new_shape):
  return LazyBuffer(new_shape, ReduceOps, LazyOp(op, [x], new_shape))

def processing_op(op, x, w, C):
  return LazyBuffer(C.out_shape, ProcessingOps, LazyOp(op, [x, w], C))
