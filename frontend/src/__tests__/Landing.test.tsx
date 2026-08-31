import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Landing from '../pages/Landing';

// Mock the 3D canvas component — WebGL/Canvas is not available in jsdom
vi.mock('../components/Hero3DBackground', () => ({
  default: () => null,
}));

describe('Landing Page', () => {
  it('renders the main heading', () => {
    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    );
    expect(screen.getByText(/Your AI Navigator/i)).toBeInTheDocument();
  });
});
