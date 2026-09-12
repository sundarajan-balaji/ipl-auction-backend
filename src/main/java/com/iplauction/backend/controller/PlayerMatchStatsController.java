package com.iplauction.backend.controller;

import com.iplauction.backend.dto.PlayerCareerStatsResponse;
import com.iplauction.backend.dto.PlayerMatchStatsResponse;
import com.iplauction.backend.dto.PlayerSeasonStatsResponse;
import com.iplauction.backend.service.PlayerMatchStatsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/player-match-stats")
@RequiredArgsConstructor
public class PlayerMatchStatsController {

    private final PlayerMatchStatsService playerMatchStatsService;

    @GetMapping
    public List<PlayerMatchStatsResponse> getAll() {
        return playerMatchStatsService.getAll();
    }

    @GetMapping("/{id}")
    public PlayerMatchStatsResponse getById(@PathVariable Long id) {
        return playerMatchStatsService.getById(id);
    }

    @GetMapping("/player/{playerId}")
    public List<PlayerMatchStatsResponse> getStatsByPlayerId(@PathVariable Long playerId) {
        return playerMatchStatsService.getStatsByPlayerId(playerId);
    }

    @GetMapping("/match/{matchId}")
    public List<PlayerMatchStatsResponse> getStatsByMatchId(@PathVariable Long matchId) {
        return playerMatchStatsService.getStatsByMatchId(matchId);
    }

    @GetMapping("/career/{playerId}")
    public PlayerCareerStatsResponse getCareerStats(@PathVariable Long playerId) {
        return playerMatchStatsService.getCareerStats(playerId);
    }

    @GetMapping("/season/{playerId}")
    public List<PlayerSeasonStatsResponse> getSeasonStats(@PathVariable Long playerId) {
        return playerMatchStatsService.getSeasonStats(playerId);
    }
}