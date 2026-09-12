package com.iplauction.backend.service;

import com.iplauction.backend.dto.PlayerCareerStatsResponse;
import com.iplauction.backend.dto.PlayerMatchStatsResponse;
import com.iplauction.backend.dto.PlayerSeasonStatsResponse;
import com.iplauction.backend.entity.PlayerMatchStats;
import com.iplauction.backend.exception.ResourceNotFoundException;
import com.iplauction.backend.repository.MatchRepository;
import com.iplauction.backend.repository.PlayerMatchStatsRepository;
import com.iplauction.backend.repository.PlayerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

@Service
@RequiredArgsConstructor
public class PlayerMatchStatsService {

    private final PlayerMatchStatsRepository playerMatchStatsRepository;
    private final PlayerRepository playerRepository;
    private final MatchRepository matchRepository;

    public List<PlayerMatchStatsResponse> getAll() {
        return playerMatchStatsRepository.findAll()
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public List<PlayerMatchStatsResponse> getStatsByPlayerId(Long playerId) {

        playerRepository.findById(playerId)
                .orElseThrow(() -> new ResourceNotFoundException("Player not found with id: " + playerId));

        return playerMatchStatsRepository.findByPlayer_Id(playerId)
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public List<PlayerMatchStatsResponse> getStatsByMatchId(Long matchId) {

        matchRepository.findById(matchId)
                .orElseThrow(() ->
                        new ResourceNotFoundException(
                                "Match not found with id: " + matchId
                        )
                );

        return playerMatchStatsRepository.findByMatch_Id(matchId)
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public PlayerMatchStatsResponse getById(Long id) {
        PlayerMatchStats stats = playerMatchStatsRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Player match stats not found with id: " + id));

        return toResponse(stats);
    }

    private PlayerMatchStatsResponse toResponse(PlayerMatchStats stats) {
        return new PlayerMatchStatsResponse(
                stats.getId(),
                stats.getMatch().getId(),
                stats.getPlayer().getId(),
                stats.getTeam().getId(),
                stats.getBattingInnings(),
                stats.getRuns(),
                stats.getBallsFaced(),
                stats.getFours(),
                stats.getSixes(),
                stats.getDismissals(),
                stats.getBowlingInnings(),
                stats.getRunsConceded(),
                stats.getBallsBowled(),
                stats.getWickets(),
                stats.getMaidens(),
                stats.getCatches(),
                stats.getStumpings(),
                stats.getRunOuts()
        );
    }

    private PlayerSeasonStatsResponse toSeasonResponse(Long playerId, Object[] result) {

        long runs = ((Number) result[3]).longValue();
        long ballsFaced = ((Number) result[4]).longValue();
        long dismissals = ((Number) result[7]).longValue();

        long runsConceded = ((Number) result[9]).longValue();
        long ballsBowled = ((Number) result[10]).longValue();
        long wickets = ((Number) result[11]).longValue();

        BigDecimal battingAverage = calculateBattingAverage(runs, dismissals);
        BigDecimal strikeRate = calculateStrikeRate(runs, ballsFaced);
        BigDecimal bowlingAverage = calculateBowlingAverage(runsConceded, wickets);
        BigDecimal economyRate = calculateEconomyRate(runsConceded, ballsBowled);

        return new PlayerSeasonStatsResponse(
                playerId,
                (String) result[0],

                ((Number) result[1]).longValue(),
                ((Number) result[2]).longValue(),
                runs,
                ballsFaced,
                ((Number) result[5]).longValue(),
                ((Number) result[6]).longValue(),
                dismissals,

                battingAverage,
                strikeRate,

                ((Number) result[8]).longValue(),
                runsConceded,
                ballsBowled,
                wickets,
                ((Number) result[12]).longValue(),

                bowlingAverage,
                economyRate,

                ((Number) result[13]).longValue(),
                ((Number) result[14]).longValue(),
                ((Number) result[15]).longValue()
        );
    }

    private BigDecimal calculateBattingAverage(long runs, long dismissals) {
        if (dismissals == 0) {
            return null;
        }

        return BigDecimal.valueOf(runs).divide(BigDecimal.valueOf(dismissals), 2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateStrikeRate(long runs, long ballsFaced) {
        if (ballsFaced == 0) {
            return null;
        }

        return BigDecimal.valueOf(runs).multiply(BigDecimal.valueOf(100)).divide(BigDecimal.valueOf(ballsFaced), 2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateBowlingAverage(long runsConceded, long wickets) {
        if (wickets == 0) {
            return null;
        }

        return BigDecimal.valueOf(runsConceded)
                .divide(BigDecimal.valueOf(wickets), 2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateEconomyRate(long runsConceded, long ballsBowled) {
        if (ballsBowled == 0) {
            return null;
        }

        return BigDecimal.valueOf(runsConceded)
                .multiply(BigDecimal.valueOf(6))
                .divide(BigDecimal.valueOf(ballsBowled), 2, RoundingMode.HALF_UP);
    }

    public PlayerCareerStatsResponse getCareerStats(Long playerId) {

        playerRepository.findById(playerId)
                .orElseThrow(() -> new ResourceNotFoundException("Player not found with id: " + playerId));

        List<Object[]> results = playerMatchStatsRepository.getCareerStats(playerId);

        Object[] result = results.get(0);


        BigDecimal battingAverage = calculateBattingAverage(
                ((Number) result[2]).longValue(),
                ((Number) result[6]).longValue()
        );

        BigDecimal strikeRate = calculateStrikeRate(
                ((Number) result[2]).longValue(),
                ((Number) result[3]).longValue()
        );

        BigDecimal bowlingAverage = calculateBowlingAverage(
                ((Number) result[8]).longValue(),
                ((Number) result[10]).longValue()
        );

        BigDecimal economyRate = calculateEconomyRate(
                ((Number) result[8]).longValue(),
                ((Number) result[9]).longValue()
        );

        return new PlayerCareerStatsResponse(
                playerId,

                ((Number) result[0]).longValue(),
                ((Number) result[1]).longValue(),
                ((Number) result[2]).longValue(),
                ((Number) result[3]).longValue(),
                ((Number) result[4]).longValue(),
                ((Number) result[5]).longValue(),
                ((Number) result[6]).longValue(),

                battingAverage,
                strikeRate,

                ((Number) result[7]).longValue(),
                ((Number) result[8]).longValue(),
                ((Number) result[9]).longValue(),
                ((Number) result[10]).longValue(),
                ((Number) result[11]).longValue(),

                bowlingAverage,
                economyRate,

                ((Number) result[12]).longValue(),
                ((Number) result[13]).longValue(),
                ((Number) result[14]).longValue()
        );
    }

    public List<PlayerSeasonStatsResponse> getSeasonStats(Long playerId) {

        playerRepository.findById(playerId)
                .orElseThrow(() ->
                        new ResourceNotFoundException(
                                "Player not found with id: " + playerId
                        )
                );

        return playerMatchStatsRepository.getSeasonStats(playerId)
                .stream()
                .map(result -> toSeasonResponse(playerId, result))
                .toList();
    }
}