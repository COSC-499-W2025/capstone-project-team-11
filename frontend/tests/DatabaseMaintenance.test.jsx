import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import axios from "axios";
import DatabaseMaintenance from "../src/DatabaseMaintenance.jsx";
import { showModal } from "../src/modal";
import { API_BASE_URL } from "../src/api";

vi.mock("axios");
vi.mock("../src/modal", () => ({
  showModal: vi.fn(),
}));

describe("DatabaseMaintenance", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("renders page and loads database tables", async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        projects: [
          {
            id: 1,
            name: "demo_project",
            scan_count: 1,
            file_count: 5,
            skills: ["React"],
          },
        ],
      },
    });

    render(<DatabaseMaintenance onBack={() => {}} />);

    // page loads
    expect(await screen.findByText(/Database Management/i)).toBeInTheDocument();

    // expand Projects section (now collapsed by default)
    const sectionButton = await screen.findByRole("button", {
      name: /Projects/i,
    });

    fireEvent.click(sectionButton);

    // now data should appear
    expect(await screen.findByText(/demo_project/i)).toBeInTheDocument();
  });

  test("refresh database button reloads tables", async () => {
    axios.get
      .mockResolvedValueOnce({ data: { projects: [] } })
      .mockResolvedValueOnce({ data: { projects: [] } });

    render(<DatabaseMaintenance onBack={() => {}} />);

    const refreshButton = await screen.findByRole("button", {
      name: /Refresh Database/i,
    });

    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  test("toggles section visibility when clicked", async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        projects: [
          {
            name: "demo_project",
            scan_count: 1,
            file_count: 5,
            skills: [],
          },
        ],
      },
    });

    render(<DatabaseMaintenance onBack={() => {}} />);

    const sectionButton = await screen.findByRole("button", {
      name: /Projects/i,
    });

    // expand
    fireEvent.click(sectionButton);

    expect(await screen.findByText(/demo_project/i)).toBeInTheDocument();

    // collapse
    fireEvent.click(sectionButton);

    await waitFor(() => {
      expect(screen.queryByText(/demo_project/i)).not.toBeInTheDocument();
    });

    // expand again
    fireEvent.click(sectionButton);

    expect(await screen.findByText(/demo_project/i)).toBeInTheDocument();
  });

  test("clear database calls modal", async () => {
    axios.get.mockResolvedValueOnce({ data: {} });

    showModal.mockResolvedValueOnce(false);

    render(<DatabaseMaintenance onBack={() => {}} />);

    const clearButton = await screen.findByRole("button", {
      name: /Clear Database/i,
    });

    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(showModal).toHaveBeenCalled();
    });
  });

  test("confirm clear database calls delete API", async () => {
    axios.get
      .mockResolvedValueOnce({ data: {} })
      .mockResolvedValueOnce({ data: {} });

    axios.delete.mockResolvedValueOnce({
      data: { message: "Database cleared" },
    });

    // simulate user confirming
    showModal.mockResolvedValueOnce(true);

    render(<DatabaseMaintenance onBack={() => {}} />);

    const clearButton = await screen.findByRole("button", {
      name: /Clear Database/i,
    });

    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalledWith(
        `${API_BASE_URL}/database/clear`
      );
    });
  });
});