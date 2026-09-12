package com.iplauction.backend.dto;

public record PlayerMatchStatsResponse(
        Long id,

        Long matchId,
        Long playerId,
        Long teamId,

        Integer battingInnings,
        Integer runs,
        Integer ballsFaced,
        Integer fours,
        Integer sixes,
        Integer dismissals,

        Integer bowlingInnings,
        Integer runsConceded,
        Integer ballsBowled,
        Integer wickets,
        Integer maidens,

        Integer catches,
        Integer stumpings,
        Integer runOuts
) {
}