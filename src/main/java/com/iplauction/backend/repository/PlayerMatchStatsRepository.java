package com.iplauction.backend.repository;

import com.iplauction.backend.entity.PlayerMatchStats;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface PlayerMatchStatsRepository extends JpaRepository<PlayerMatchStats, Long> {
    @EntityGraph(attributePaths = {
            "match",
            "player",
            "team"
    })
    List<PlayerMatchStats> findByPlayer_Id(Long playerId);

    @EntityGraph(attributePaths = {
            "match",
            "player",
            "team"
    })
    List<PlayerMatchStats> findByMatch_Id(Long matchId);

    @Query("""
        SELECT
            COUNT(s.id),
            COALESCE(SUM(s.battingInnings), 0),
            COALESCE(SUM(s.runs), 0),
            COALESCE(SUM(s.ballsFaced), 0),
            COALESCE(SUM(s.fours), 0),
            COALESCE(SUM(s.sixes), 0),
            COALESCE(SUM(s.dismissals), 0),
            COALESCE(SUM(s.bowlingInnings), 0),
            COALESCE(SUM(s.runsConceded), 0),
            COALESCE(SUM(s.ballsBowled), 0),
            COALESCE(SUM(s.wickets), 0),
            COALESCE(SUM(s.maidens), 0),
            COALESCE(SUM(s.catches), 0),
            COALESCE(SUM(s.stumpings), 0),
            COALESCE(SUM(s.runOuts), 0)
        FROM PlayerMatchStats s
        WHERE s.player.id = :playerId
        """)
    List<Object[]> getCareerStats(@Param("playerId") Long playerId);

    @Query("""
        SELECT
            m.season,
            COUNT(s.id),
            COALESCE(SUM(s.battingInnings), 0),
            COALESCE(SUM(s.runs), 0),
            COALESCE(SUM(s.ballsFaced), 0),
            COALESCE(SUM(s.fours), 0),
            COALESCE(SUM(s.sixes), 0),
            COALESCE(SUM(s.dismissals), 0),
            COALESCE(SUM(s.bowlingInnings), 0),
            COALESCE(SUM(s.runsConceded), 0),
            COALESCE(SUM(s.ballsBowled), 0),
            COALESCE(SUM(s.wickets), 0),
            COALESCE(SUM(s.maidens), 0),
            COALESCE(SUM(s.catches), 0),
            COALESCE(SUM(s.stumpings), 0),
            COALESCE(SUM(s.runOuts), 0)
        FROM PlayerMatchStats s
        JOIN s.match m
        WHERE s.player.id = :playerId
        GROUP BY m.season
        ORDER BY m.season DESC
        """)
    List<Object[]> getSeasonStats(@Param("playerId") Long playerId);
}