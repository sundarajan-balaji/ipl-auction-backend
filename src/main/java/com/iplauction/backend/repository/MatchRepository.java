package com.iplauction.backend.repository;

import com.iplauction.backend.entity.Match;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface MatchRepository extends JpaRepository<Match, Long> {

    @Override
    @EntityGraph(attributePaths = {
            "venue",
            "team1",
            "team2",
            "tossWinner",
            "winner",
            "playerOfMatch"
    })
    List<Match> findAll();

    @Override
    @EntityGraph(attributePaths = {
            "venue",
            "team1",
            "team2",
            "tossWinner",
            "winner",
            "playerOfMatch"
    })
    Optional<Match> findById(Long id);
}