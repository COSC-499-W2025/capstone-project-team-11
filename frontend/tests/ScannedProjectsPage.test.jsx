import React from "react";
import { render, screen } from "@testing-library/react";
import ScannedProjectsPage from "../src/ScannedProjectsPage.jsx";

describe("ScannedProjectsPage", () => {
  test("renders back button", async () => {
    render(<ScannedProjectsPage onBack={() => {}} />);
    const backButton = await screen.findByText(/Back to Main Menu/i);
    expect(backButton).toBeInTheDocument();
    expect(await screen.findByText(/No scanned projects yet/i)).toBeInTheDocument();
  });
});