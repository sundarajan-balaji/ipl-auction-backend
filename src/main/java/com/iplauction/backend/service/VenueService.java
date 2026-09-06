package com.iplauction.backend.service;

import com.iplauction.backend.entity.Venue;
import com.iplauction.backend.exception.ResourceNotFoundException;
import com.iplauction.backend.repository.VenueRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class VenueService {

    private final VenueRepository venueRepository;

    public List<Venue> getAllVenues() {
        return venueRepository.findAll();
    }

    public Venue getVenueById(Long id) {
        return venueRepository.findById(id)
                .orElseThrow(() ->
                        new ResourceNotFoundException(
                                "Venue not found with id: " + id));
    }
}