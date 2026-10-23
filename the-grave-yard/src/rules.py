"""Engine-independent Grave Yard game rules; GRAB adapter still required."""
from dataclasses import dataclass, field
from enum import Enum

class Phase(str, Enum):
    REST = "rest"
    HUNT = "hunt"
    ESCAPE = "escape"

@dataclass
class Player:
    alive: bool = True
    escaped: bool = False
    holding_gem: bool = False
    climbing_tree: bool = False

@dataclass
class GraveYardRound:
    rest_seconds: float = 60
    hunt_seconds: float = 60
    max_hunts: int = 5
    wipe_reset_seconds: float = 5
    phase: Phase = Phase.REST
    phase_elapsed: float = 0
    completed_hunts: int = 0
    gate_open: bool = False
    skull_placed: bool = False
    players: dict = field(default_factory=dict)
    wipe_elapsed: float = 0

    def add_player(self, player_id):
        self.players[player_id] = Player()

    def protected(self, player_id):
        # Climbing a tree does NOT confer immunity.
        return self.players[player_id].holding_gem

    def can_capture(self, player_id):
        p = self.players[player_id]
        return self.phase == Phase.HUNT and p.alive and not p.escaped and not self.protected(player_id)

    def capture(self, player_id):
        if not self.can_capture(player_id):
            return False
        self.players[player_id].alive = False
        return True

    def place_skull(self, player_id, physically_in_socket, released):
        if self.phase != Phase.ESCAPE or not physically_in_socket or not released:
            return False
        p = self.players[player_id]
        if not p.alive or p.escaped:
            return False
        self.skull_placed = True
        self.gate_open = True
        return True

    def finish(self, player_id, touched_native_finish):
        p = self.players[player_id]
        if not self.gate_open or not touched_native_finish or not p.alive:
            return False
        p.escaped = True
        return True

    def reset(self):
        self.phase = Phase.REST
        self.phase_elapsed = 0
        self.completed_hunts = 0
        self.gate_open = False
        self.skull_placed = False
        self.wipe_elapsed = 0
        for p in self.players.values():
            p.alive, p.escaped, p.holding_gem, p.climbing_tree = True, False, False, False

    def tick(self, seconds):
        if seconds < 0:
            raise ValueError("seconds must be nonnegative")
        remaining = seconds
        while remaining > 0 and self.phase != Phase.ESCAPE:
            duration = self.rest_seconds if self.phase == Phase.REST else self.hunt_seconds
            if duration <= 0:
                raise ValueError("phase duration must be positive")
            step = min(remaining, duration - self.phase_elapsed)
            self.phase_elapsed += step
            remaining -= step
            if self.phase_elapsed >= duration:
                self.phase_elapsed = 0
                if self.phase == Phase.REST:
                    self.phase = Phase.HUNT
                else:
                    self.completed_hunts += 1
                    self.phase = Phase.ESCAPE if self.completed_hunts >= self.max_hunts else Phase.REST
        if self.players and not any(p.alive for p in self.players.values()) and not any(p.escaped for p in self.players.values()):
            self.wipe_elapsed += seconds
            if self.wipe_elapsed >= self.wipe_reset_seconds:
                self.reset()
        else:
            self.wipe_elapsed = 0
