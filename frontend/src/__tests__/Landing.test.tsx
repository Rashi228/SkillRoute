import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Landing from '../pages/Landing';

// Simple test to ensure the component renders without crashing
describe('Landing Page', () => {
  it('renders the main heading', () => {
    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    );
    expect(screen.getByText(/Your Path to Mastery/i)).toBeInTheDocument();
  });
});
