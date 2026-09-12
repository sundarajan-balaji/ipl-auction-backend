package com.iplauction.backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.OffsetDateTime;

@Entity
@Table(name = "player_match_stats")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PlayerMatchStats {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "match_id", nullable = false)
    private Match match;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "player_id", nullable = false)
    private Player player;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "team_id", nullable = false)
    private Team team;

    @Column(name = "batting_innings", nullable = false)
    private Integer battingInnings;

    @Column(nullable = false)
    private Integer runs;

    @Column(name = "balls_faced", nullable = false)
    private Integer ballsFaced;

    @Column(nullable = false)
    private Integer fours;

    @Column(nullable = false)
    private Integer sixes;

    @Column(nullable = false)
    private Integer dismissals;

    @Column(name = "bowling_innings", nullable = false)
    private Integer bowlingInnings;

    @Column(name = "runs_conceded", nullable = false)
    private Integer runsConceded;

    @Column(name = "balls_bowled", nullable = false)
    private Integer ballsBowled;

    @Column(nullable = false)
    private Integer wickets;

    @Column(nullable = false)
    private Integer maidens;

    @Column(nullable = false)
    private Integer catches;

    @Column(nullable = false)
    private Integer stumpings;

    @Column(name = "run_outs", nullable = false)
    private Integer runOuts;

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt;
}