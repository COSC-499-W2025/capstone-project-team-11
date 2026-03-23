import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import axios from "axios";
import DatabaseMaintenance from "../src/DatabaseMaintenance.jsx";

vi.mock("axios");

describe("DatabaseMaintenance", () => {

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    document.querySelectorAll(".modal-overlay").forEach((node) => node.remove());
  });

  test("renders page and loads database tables", async () => {

    axios.get.mockResolvedValueOnce({
      data: {
        projects: [
          {
            id: 1,
            name: "demo_project",
            repo_url: "https://repo.com",
            scan_count: 1,
            file_count: 5,
            skills: ["React"],
            summary_text: "Test summary"
          }
        ]
      }
    });

    render(<DatabaseMaintenance onBack={() => {}} />);

    expect(screen.getByText(/Database Management/i)).toBeInTheDocument();

    expect(await screen.findByText(/projects \(1\)/i)).toBeInTheDocument();
  });

  test("refresh database button reloads tables", async () => {

    axios.get
      .mockResolvedValueOnce({
        data: { projects: [] }
      })
      .mockResolvedValueOnce({
        data: { projects: [] }
      });

    render(<DatabaseMaintenance onBack={() => {}} />);

    const refreshButton = await screen.findByRole("button", {
      name: /Refresh Database/i
    });

    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  test("expands table rows when clicked", async () => {

    axios.get.mockResolvedValueOnce({
      data: {
        projects: [
          {
            id: 1,
            name: "demo_project",
            repo_url: "repo",
            scan_count: 1,
            file_count: 5,
            skills: [],
            summary_text: "summary"
          }
        ]
      }
    });

    render(<DatabaseMaintenance onBack={() => {}} />);

    const tableButton = await screen.findByText(/projects \(1\)/i);

    fireEvent.click(tableButton);

    expect(await screen.findByText(/demo_project/i)).toBeInTheDocument();
  });

  test("clear database button opens confirmation modal", async () => {

    axios.get.mockResolvedValueOnce({
      data: { projects: [] }
    });

    render(<DatabaseMaintenance onBack={() => {}} />);

    const clearButton = await screen.findByRole("button", {
      name: /Clear Database/i
    });

    fireEvent.click(clearButton);

    expect(
      await screen.findByText(/Are you sure you want to delete all database data/i)
    ).toBeInTheDocument();
  });

  test("confirm clear database calls delete API", async () => {

    axios.get
      .mockResolvedValueOnce({ data: { projects: [] } })
      .mockResolvedValueOnce({ data: { projects: [] } });

    axios.delete.mockResolvedValueOnce({
      data: { message: "Database cleared" }
    });

    render(<DatabaseMaintenance onBack={() => {}} />);

    const clearButton = await screen.findByRole("button", {
      name: /^Clear Database$/i
    });

    fireEvent.click(clearButton);

    const confirmButton = await screen.findByRole("button", {
      name: /Yes, Clear Database/i
    });

    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalledWith(
        expect.stringMatching(/\/database\/clear$/)
      );
    });
  });

});
