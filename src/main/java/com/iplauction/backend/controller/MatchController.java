package com.iplauction.backend.controller;

import com.iplauction.backend.dto.MatchResponse;
import com.iplauction.backend.entity.Match;
import com.iplauction.backend.service.MatchService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/matches")
@RequiredArgsConstructor
public class MatchController {

    private final MatchService matchService;

    @GetMapping
    public List<MatchResponse> getAllMatches() {
        return matchService.getAllMatches()
                .stream()
                .map(MatchResponse::from)
                .toList();
    }

    @GetMapping("/{id}")
    public MatchResponse getMatchById(@PathVariable Long id) {
        Match match = matchService.getMatchById(id);
        return MatchResponse.from(match);
    }
}