package com.iplauction.backend.dto;

import com.iplauction.backend.entity.Team;

public record TeamResponse(
        Long id,
        String name,
        String shortCode
) {

    public static TeamResponse from(Team team) {
        return new TeamResponse(
                team.getId(),
                team.getName(),
                team.getShortCode()
        );
    }
}