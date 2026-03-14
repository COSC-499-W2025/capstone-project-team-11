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

  afterEach(() => {
    delete window.api;
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
          contributor_roles: { contributors: [], summary: {} },
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
          contributor_roles: { contributors: [], summary: {} },
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

    fireEvent.click(await screen.findByRole("button", { name: /Edit Project/i }));

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
    window.confirm = vi.fn(() => false);
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
          contributor_roles: { contributors: [], summary: {} },
          scans: [],
          files_summary: { total_files: 0, extensions: {} },
          evidence: [],
          llm_summary: null,
        },
      });

    render(<ScannedProjectsPage onBack={() => {}} />);

    expect(await screen.findByText(/Pretty Project Name/i)).toBeInTheDocument();

    fireEvent.click(await screen.findByRole("button", { name: /Delete Project/i }));

    expect(window.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete "Pretty Project Name"?'
    );
  });

  test("uses file picker to change thumbnail and renders preview", async () => {
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
            thumbnail_path: null,
          },
          skills: [],
          languages: [],
          contributors: [],
          contributor_roles: { contributors: [], summary: {} },
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
            custom_name: null,
            repo_url: "https://old-url.com",
            created_at: "2025-01-01",
            thumbnail_path: "/picked/thumb.png",
          },
          skills: [],
          languages: [],
          contributors: [],
          contributor_roles: { contributors: [], summary: {} },
          scans: [],
          files_summary: { total_files: 0, extensions: {} },
          evidence: [],
          llm_summary: null,
        },
      })
      .mockResolvedValueOnce({
        data: [{ id: 1, name: "demo_project", custom_name: null }],
      });

    axios.patch.mockResolvedValueOnce({ data: {} });
    window.api = {
      openThumbnailDialog: vi.fn().mockResolvedValue("/picked/thumb.png"),
    };

    render(<ScannedProjectsPage onBack={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: /Add Thumbnail/i }));

    await waitFor(() => {
      expect(window.api.openThumbnailDialog).toHaveBeenCalled();
    });
    await waitFor(() => {
      expect(axios.patch).toHaveBeenCalledWith(
        expect.stringMatching(/\/projects\/1$/),
        { thumbnail_path: "/picked/thumb.png" }
      );
    });
    expect(await screen.findByRole("img", { name: /demo_project thumbnail/i })).toHaveAttribute(
      "src",
      "http://127.0.0.1:8000/projects/1/thumbnail/image?v=%2Fpicked%2Fthumb.png"
    );
  });

  test("renders contributor role assignments in project details", async () => {
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
            repo_url: null,
            created_at: "2025-01-01",
            thumbnail_path: null,
          },
          skills: [],
          languages: ["Python"],
          contributors: ["alice"],
          contributor_roles: {
            contributors: [
              {
                name: "alice",
                primary_role: "Backend Developer",
                role_description: "Develops and maintains server-side systems, APIs, and business logic",
                secondary_roles: ["Quality Assurance Developer"],
                confidence: 0.82,
              },
            ],
            summary: {
              team_composition: "1 Backend Developer",
            },
          },
          scans: [],
          files_summary: { total_files: 3, extensions: { ".py": 3 } },
          evidence: [],
          llm_summary: null,
        },
      });

    render(<ScannedProjectsPage onBack={() => {}} />);

    expect(await screen.findByText(/^Contributor Roles$/i)).toBeInTheDocument();
    expect(
      await screen.findByText(
        (content, element) =>
          element?.classList?.contains("contributor-role-primary") &&
          content.includes("Backend Developer")
      )
    ).toBeInTheDocument();
    expect(await screen.findByText(/Confidence: 82%/i)).toBeInTheDocument();
    expect(await screen.findByText(/Team Composition: 1 Backend Developer/i)).toBeInTheDocument();
  });
});
