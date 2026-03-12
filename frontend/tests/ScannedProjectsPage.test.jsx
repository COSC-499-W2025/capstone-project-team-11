import React from "react";
import { render, screen } from "@testing-library/react";
import ScannedProjectsPage from "../src/ScannedProjectsPage.jsx";

describe("ScannedProjectsPage", () => {
  test("renders back button", () => {
    render(<ScannedProjectsPage onBack={() => {}} />);
    const backButton = screen.getByText(/Back to Main Menu/i);
    expect(backButton).toBeInTheDocument();
  });
});