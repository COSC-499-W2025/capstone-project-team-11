import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import ScannedProjectsPage from "../src/ScannedProjectsPage.jsx";

vi.mock("axios");

describe("ScannedProjectsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.alert = vi.fn();
    window.confirm = vi.fn(() => true);
  });

  test("renders back button and empty state", async () => {
    axios.get.mockResolvedValueOnce({ data: [] });

    render(<ScannedProjectsPage onBack={() => {}} />);

    expect(await screen.findByText(/Back to Main Menu/i)).toBeInTheDocument();
    expect(await screen.findByText(/No scanned projects yet/i)).toBeInTheDocument();
  });

  test("edits and saves project info", async () => {
    axios.get
      .mockResolvedValueOnce({
        data: [{ id: 1, name: "demo_project", custom_name: null }],
      })
      .mockResolvedValueOnce({
        data: {
          project: {
            id: 1,
            name: "demo_project",
            custom_name: null,
            repo_url: "https://old-url.com",
            created_at: "2025-01-01",
            thumbnail_path: "/old/thumb.png",
          },
          skills: [],
          languages: [],
          contributors: [],
          scans: [],
          files_summary: { total_files: 0, extensions: {} },
          evidence: [],
          llm_summary: null,
        },
      })
      .mockResolvedValueOnce({
        data: {
          project: {
            id: 1,
            name: "demo_project",
            custom_name: "Updated Display Name",
            repo_url: "https://new-url.com",
            created_at: "2025-01-01",
            thumbnail_path: "/new/thumb.png",
          },
          skills: [],
          languages: [],
          contributors: [],
          scans: [],
          files_summary: { total_files: 0, extensions: {} },
          evidence: [],
          llm_summary: null,
        },
      })
      .mockResolvedValueOnce({
        data: [{ id: 1, name: "demo_project", custom_name: "Updated Display Name" }],
      });

    axios.patch.mockResolvedValueOnce({
      data: {
        project: {
          id: 1,
          name: "demo_project",
          custom_name: "Updated Display Name",
          repo_url: "https://new-url.com",
          thumbnail_path: "/new/thumb.png",
        },
      },
    });

    render(<ScannedProjectsPage onBack={() => {}} />);

    expect(await screen.findByText(/demo_project/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Edit Project/i }));

    const displayNameInput = await screen.findByDisplayValue("");
    const repoUrlInput = screen.getByDisplayValue("https://old-url.com");
    const thumbnailInput = screen.getByDisplayValue("/old/thumb.png");

    fireEvent.change(displayNameInput, { target: { value: "Updated Display Name" } });
    fireEvent.change(repoUrlInput, { target: { value: "https://new-url.com" } });
    fireEvent.change(thumbnailInput, { target: { value: "/new/thumb.png" } });

    fireEvent.click(screen.getByRole("button", { name: /Save Changes/i }));

    await waitFor(() => {
      expect(axios.patch).toHaveBeenCalledWith(
        expect.stringMatching(/\/projects\/1$/),
        {
          custom_name: "Updated Display Name",
          repo_url: "https://new-url.com",
          thumbnail_path: "/new/thumb.png",
        }
      );
    });

    expect(window.alert).toHaveBeenCalledWith("Project updated successfully");
  });

  test("delete confirmation uses project name", async () => {
    axios.get
      .mockResolvedValueOnce({
        data: [{ id: 1, name: "demo_project", custom_name: "Pretty Project Name" }],
      })
      .mockResolvedValueOnce({
        data: {
          project: {
            id: 1,
            name: "demo_project",
            custom_name: "Pretty Project Name",
            repo_url: null,
            created_at: "2025-01-01",
            thumbnail_path: null,
          },
          skills: [],
          languages: [],
          contributors: [],
          scans: [],
          files_summary: { total_files: 0, extensions: {} },
          evidence: [],
          llm_summary: null,
        },
      });

    axios.delete.mockResolvedValueOnce({ data: { message: "Project deleted successfully" } });

    render(<ScannedProjectsPage onBack={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: /Delete Project/i }));

    expect(window.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete "Pretty Project Name"?'
    );
  });
});