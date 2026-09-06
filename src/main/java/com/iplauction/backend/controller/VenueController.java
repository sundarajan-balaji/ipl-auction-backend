package com.iplauction.backend.controller;

import com.iplauction.backend.dto.VenueResponse;
import com.iplauction.backend.entity.Venue;
import com.iplauction.backend.service.VenueService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/venues")
@RequiredArgsConstructor
public class VenueController {

    private final VenueService venueService;

    @GetMapping
    public List<VenueResponse> getAllVenues() {
        return venueService.getAllVenues()
                .stream()
                .map(VenueResponse::from)
                .toList();
    }

    @GetMapping("/{id}")
    public VenueResponse getVenueById(@PathVariable Long id) {
        Venue venue = venueService.getVenueById(id);
        return VenueResponse.from(venue);
    }
}