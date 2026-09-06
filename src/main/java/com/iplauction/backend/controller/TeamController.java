package com.iplauction.backend.controller;

import com.iplauction.backend.dto.TeamResponse;
import com.iplauction.backend.entity.Team;
import com.iplauction.backend.service.TeamService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/teams")
@RequiredArgsConstructor
public class TeamController {

    private final TeamService teamService;

    @GetMapping
    public List<TeamResponse> getAllTeams() {
        return teamService.getAllTeams()
                .stream()
                .map(TeamResponse::from)
                .toList();
    }

    @GetMapping("/{id}")
    public TeamResponse getTeamById(@PathVariable Long id) {
        Team team = teamService.getTeamById(id);
        return TeamResponse.from(team);
    }
}