package com.iplauction.backend.dto;

import java.math.BigDecimal;

public record PlayerSeasonStatsResponse(
        Long playerId,
        String season,

        Long matches,
        Long battingInnings,
        Long runs,
        Long ballsFaced,
        Long fours,
        Long sixes,
        Long dismissals,

        BigDecimal battingAverage,
        BigDecimal strikeRate,

        Long bowlingInnings,
        Long runsConceded,
        Long ballsBowled,
        Long wickets,
        Long maidens,

        BigDecimal bowlingAverage,
        BigDecimal economyRate,

        Long catches,
        Long stumpings,
        Long runOuts
) {
}