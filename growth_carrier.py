"""Finite CPU continuation over explicit relations in one dense mmap body.

An address locates a record for the machine; it has no spatial meaning.  Every
material continuation, available free contact and upper slot is stored as an
explicit handle.  The instruction locus executing ``collision`` is the moving
cause; no gesture or kinetic value is carried beside it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import mmap
from pathlib import Path
import struct


FREE = 0
GESTURE_0 = -1
GESTURE_1 = 1
GESTURES = (GESTURE_0, GESTURE_1)
NO_HANDLE = (1 << 32) - 1

_MAGIC = b"LGROWV06"
_HEADER = struct.Struct("<8sII")
# A free place keeps its physical contact but has no conducting port.  Growth
# opens that already-present contact and leaves its birth relation.  A return
# relation records actual passage through old body; upper names a directly
# attached free material slot rather than a position derived from an address.
_RECORD = struct.Struct("<b3xIIIII")
HEADER_BYTES = _HEADER.size
RECORD_BYTES = _RECORD.size


@dataclass(frozen=True)
class Place:
    address: int


@dataclass(frozen=True)
class MaterialRecord:
    gesture: int
    contact_handle: int = NO_HANDLE
    port_handle: int = NO_HANDLE
    birth_handle: int = NO_HANDLE
    return_handle: int = NO_HANDLE
    upper_handle: int = NO_HANDLE

    @property
    def free(self) -> bool:
        return self.gesture == FREE

    @property
    def born_here(self) -> bool:
        return self.birth_handle != NO_HANDLE

    @property
    def carries_return(self) -> bool:
        return self.return_handle != NO_HANDLE


class CollisionKind(str, Enum):
    PASS = "pass"
    MATERIALIZE = "materialize"
    RETRACT = "retract"
    REFLECT = "reflect"
    HALT = "halt"


@dataclass(frozen=True)
class Collision:
    kind: CollisionKind
    current: Place
    met: Place | None
    continuation: Place | None
    changed: tuple[Place, ...]


@dataclass(frozen=True)
class LaneStop:
    start: Place
    final: Place | None
    collisions: int
    halted: bool


@dataclass(frozen=True)
class LaneRun:
    stop: LaneStop
    trace: tuple[Collision, ...]


class MmapBody:
    """One file-backed material surface whose handles are opaque relations."""

    def __init__(self, path: Path, stream, mapping: mmap.mmap, capacity: int):
        self.path = Path(path)
        self._stream = stream
        self._mmap = mapping
        self.capacity = int(capacity)

    @classmethod
    def create(cls, path: str | Path, capacity: int) -> "MmapBody":
        path = Path(path)
        if capacity < 1:
            raise ValueError("body needs at least one material place")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as stream:
            stream.truncate(HEADER_BYTES + int(capacity) * RECORD_BYTES)
        body = cls.open(path)
        body._mmap[:HEADER_BYTES] = _HEADER.pack(
            _MAGIC,
            int(capacity),
            RECORD_BYTES,
        )
        for address in range(int(capacity)):
            body._store(address, MaterialRecord(FREE))
        body.flush()
        return body

    @classmethod
    def open(cls, path: str | Path) -> "MmapBody":
        path = Path(path)
        stream = path.open("r+b", buffering=0)
        mapping = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_WRITE)
        magic, capacity, record_bytes = _HEADER.unpack(mapping[:HEADER_BYTES])
        if magic not in (_MAGIC, b"\0" * len(_MAGIC)):
            mapping.close()
            stream.close()
            raise ValueError("not an explicit-relation growth body")
        if magic == _MAGIC and record_bytes != RECORD_BYTES:
            mapping.close()
            stream.close()
            raise ValueError("material ABI mismatch")
        if magic == b"\0" * len(_MAGIC):
            capacity = (len(mapping) - HEADER_BYTES) // RECORD_BYTES
        return cls(path, stream, mapping, int(capacity))

    def __enter__(self) -> "MmapBody":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def close(self) -> None:
        self.flush()
        self._mmap.close()
        self._stream.close()

    def flush(self) -> None:
        self._mmap.flush()

    def snapshot(self) -> bytes:
        """Read-only witness; the collision law never calls this method."""
        return bytes(self._mmap)

    def record_bytes(self, address: int) -> bytes:
        offset = self._offset(address)
        return bytes(self._mmap[offset : offset + RECORD_BYTES])

    def read(self, place: int | Place) -> MaterialRecord:
        address = place.address if isinstance(place, Place) else int(place)
        values = _RECORD.unpack_from(self._mmap, self._offset(address))
        return MaterialRecord(*map(int, values))

    def place_relation(
        self,
        address: int,
        gesture: int,
        target: int,
        *,
        upper_slot: int = NO_HANDLE,
    ) -> None:
        """External preparation of an already conducting body relation."""
        if gesture not in GESTURES:
            raise ValueError("a material relation needs one of two gestures")
        self._store(
            address,
            MaterialRecord(
                gesture=gesture,
                contact_handle=int(target),
                port_handle=int(target),
                upper_handle=int(upper_slot),
            ),
        )

    def place_free_contact(self, address: int, target: int) -> None:
        """Expose directly adjacent free matter without making it conduct."""
        record = self.read(address)
        if not record.free:
            raise ValueError("only free matter can receive a passive contact")
        self._store(
            address,
            MaterialRecord(
                gesture=FREE,
                contact_handle=int(target),
                upper_handle=record.upper_handle,
            ),
        )

    def place_unbound(self, address: int, gesture: int) -> None:
        """External placement without a conducting or available relation."""
        if gesture not in GESTURES:
            raise ValueError("material needs one of two gestures")
        self._store(address, MaterialRecord(gesture))

    def clear_place(self, address: int) -> None:
        """External scalpel: remove matter but preserve its physical contacts."""
        record = self.read(address)
        self._store(
            address,
            MaterialRecord(
                gesture=FREE,
                contact_handle=record.contact_handle,
                upper_handle=record.upper_handle,
            ),
        )

    def resolve(self, handle: int) -> Place | None:
        if int(handle) == NO_HANDLE:
            return None
        if not 0 <= int(handle) < self.capacity:
            return None
        return Place(int(handle))

    def contact(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.contact_handle)

    def port(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.port_handle)

    def back(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.birth_handle)

    def return_from(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.return_handle)

    def upper_slot(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.upper_handle)

    def _offset(self, address: int) -> int:
        if not 0 <= int(address) < self.capacity:
            raise IndexError(address)
        return HEADER_BYTES + int(address) * RECORD_BYTES

    def _store(self, place: int | Place, record: MaterialRecord) -> None:
        address = place.address if isinstance(place, Place) else int(place)
        if record.gesture not in (FREE, *GESTURES):
            raise ValueError("invalid material gesture")
        handles = (
            record.contact_handle,
            record.port_handle,
            record.birth_handle,
            record.return_handle,
            record.upper_handle,
        )
        for handle in handles:
            if handle != NO_HANDLE:
                self._offset(handle)
        _RECORD.pack_into(
            self._mmap,
            self._offset(address),
            int(record.gesture),
            *map(int, handles),
        )


def _retract_one(
    body: MmapBody,
    current: Place,
    here: MaterialRecord,
    obstacle: Place | None,
) -> Collision:
    """One local return through the relation left by actual materialization."""
    previous = body.back(here)
    if previous is None:
        return Collision(CollisionKind.REFLECT, current, obstacle, None, ())

    changed: list[Place] = [current]
    body._store(
        current,
        MaterialRecord(
            gesture=FREE,
            contact_handle=here.contact_handle,
            upper_handle=here.upper_handle,
        ),
    )
    previous_record = body.read(previous)

    if previous_record.born_here:
        body._store(
            previous,
            MaterialRecord(
                gesture=previous_record.gesture,
                contact_handle=previous_record.contact_handle,
                port_handle=previous_record.birth_handle,
                birth_handle=previous_record.birth_handle,
                return_handle=previous_record.return_handle,
                upper_handle=previous_record.upper_handle,
            ),
        )
        changed.append(previous)
        continuation: Place | None = previous
    else:
        continuation = None

    return Collision(
        CollisionKind.RETRACT,
        current,
        previous,
        continuation,
        tuple(changed),
    )


def _materialize_upper_entry(
    body: MmapBody,
    current: Place,
    met: Place,
    met_record: MaterialRecord,
) -> Place | None:
    """Materialize the explicitly attached upper slot at a closed junction."""
    if met_record.born_here or body.return_from(met_record) != current:
        return None
    first = body.port(met_record)
    if first is None:
        return None
    first_record = body.read(first)
    if not first_record.born_here or body.back(first_record) != met:
        return None
    upper = body.upper_slot(met_record)
    if upper is None:
        return None
    upper_record = body.read(upper)
    if not upper_record.free or body.contact(upper_record) != met:
        return None
    body._store(
        upper,
        MaterialRecord(
            gesture=-met_record.gesture,
            contact_handle=upper_record.contact_handle,
            port_handle=upper_record.contact_handle,
            upper_handle=upper_record.upper_handle,
        ),
    )
    return upper


def collision(body: MmapBody, current: Place) -> Collision:
    """Perform one local contact using only explicit directly attached handles."""
    here = body.read(current)
    if here.free:
        return Collision(CollisionKind.HALT, current, None, None, ())

    if here.born_here and here.port_handle == here.birth_handle:
        return _retract_one(body, current, here, body.back(here))

    met = body.port(here)
    if met is None:
        if here.born_here:
            return _retract_one(body, current, here, None)
        return Collision(CollisionKind.HALT, current, None, None, ())

    met_record = body.read(met)
    if met_record.free:
        body._store(
            met,
            MaterialRecord(
                gesture=-here.gesture,
                contact_handle=met_record.contact_handle,
                port_handle=met_record.contact_handle,
                birth_handle=current.address,
                upper_handle=met_record.upper_handle,
            ),
        )
        return Collision(
            CollisionKind.MATERIALIZE,
            current,
            met,
            met,
            (met,),
        )

    if met_record.gesture == -here.gesture:
        changed: list[Place] = []
        if (
            (here.born_here or here.carries_return)
            and not met_record.born_here
            and not met_record.carries_return
        ):
            met_record = MaterialRecord(
                gesture=met_record.gesture,
                contact_handle=met_record.contact_handle,
                port_handle=met_record.port_handle,
                birth_handle=met_record.birth_handle,
                return_handle=current.address,
                upper_handle=met_record.upper_handle,
            )
            body._store(met, met_record)
            changed.append(met)

        upper = _materialize_upper_entry(body, current, met, met_record)
        if upper is not None:
            changed.append(upper)
            return Collision(
                CollisionKind.MATERIALIZE,
                current,
                met,
                met,
                tuple(changed),
            )
        return Collision(CollisionKind.PASS, current, met, met, tuple(changed))

    if here.born_here:
        return _retract_one(body, current, here, met)
    return Collision(CollisionKind.REFLECT, current, met, None, ())


def execute_lane(
    body: MmapBody,
    start: Place,
    collision_limit: int,
    *,
    capture_trace: bool = False,
) -> LaneRun:
    """Run one finite CPU continuation by following only material handles."""
    if collision_limit < 0:
        raise ValueError("collision limit must be non-negative")
    current: Place | None = start
    completed = 0
    observed: list[Collision] | None = [] if capture_trace else None
    while current is not None and completed < collision_limit:
        event = collision(body, current)
        current = event.continuation
        completed += 1
        if observed is not None:
            observed.append(event)
    return LaneRun(
        LaneStop(start, current, completed, current is None),
        tuple(observed or ()),
    )
