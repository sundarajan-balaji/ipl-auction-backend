package com.iplauction.backend.dto;

import com.iplauction.backend.entity.Venue;

public record VenueResponse(
        Long id,
        String name,
        String city,
        String country
) {

    public static VenueResponse from(Venue venue) {
        return new VenueResponse(
                venue.getId(),
                venue.getName(),
                venue.getCity(),
                venue.getCountry()
        );
    }
}