package com.iplauction.backend.dto;

import com.iplauction.backend.entity.Match;

import java.time.LocalDate;

public record MatchResponse(
        Long id,
        Long sourceMatchId,
        String season,
        LocalDate matchDate,
        String city,

        Long venueId,
        String venueName,

        Long team1Id,
        String team1Name,

        Long team2Id,
        String team2Name,

        Long tossWinnerTeamId,
        String tossWinnerTeamName,
        String tossDecision,

        Long winnerTeamId,
        String winnerTeamName,

        String resultType,
        Integer resultMargin,

        Long playerOfMatchId,
        String playerOfMatchName
) {

    public static MatchResponse from(Match match) {
        return new MatchResponse(
                match.getId(),
                match.getSourceMatchId(),
                match.getSeason(),
                match.getMatchDate(),
                match.getCity(),

                match.getVenue().getId(),
                match.getVenue().getName(),

                match.getTeam1().getId(),
                match.getTeam1().getName(),

                match.getTeam2().getId(),
                match.getTeam2().getName(),

                match.getTossWinner() != null
                        ? match.getTossWinner().getId()
                        : null,

                match.getTossWinner() != null
                        ? match.getTossWinner().getName()
                        : null,

                match.getTossDecision(),

                match.getWinner() != null
                        ? match.getWinner().getId()
                        : null,

                match.getWinner() != null
                        ? match.getWinner().getName()
                        : null,

                match.getResultType(),
                match.getResultMargin(),

                match.getPlayerOfMatch() != null
                        ? match.getPlayerOfMatch().getId()
                        : null,

                match.getPlayerOfMatch() != null
                        ? match.getPlayerOfMatch().getName()
                        : null
        );
    }
}