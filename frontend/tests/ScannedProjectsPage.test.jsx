import React from "react";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
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

  test("renders dashboard details and supports search plus tabs", async () => {
    axios.get
      .mockResolvedValueOnce({
        data: [
          { id: 1, name: "demo_project", custom_name: "Pretty Demo" },
          { id: 2, name: "beta_project", custom_name: null },
        ],
      })
      .mockResolvedValueOnce({
        data: {
          project: {
            id: 1,
            name: "demo_project",
            custom_name: "Pretty Demo",
            repo_url: "https://example.com/demo",
            created_at: "2025-01-01",
            thumbnail_path: "/old/thumb.png",
          },
          skills: ["Testing"],
          languages: ["Python"],
          contributors: ["alice"],
          contributor_roles: {
            contributors: [
              {
                name: "alice",
                primary_role: "Backend Developer",
                role_description: "Builds API and service logic",
                secondary_roles: ["Quality Assurance Developer"],
                confidence: 0.82,
              },
            ],
            summary: {
              team_composition: "1 Backend Developer",
            },
          },
          scans: [{ scanned_at: "2026-02-04T10:00:00Z", notes: "Nightly scan" }],
          files_summary: { total_files: 3, extensions: { ".py": 3 } },
          evidence: [{ description: "Won hackathon", type: "award", value: "winner" }],
          llm_summary: {
            text: "Interactive dashboard for project analytics.",
            updated_at: "2026-02-03T10:00:00Z",
          },
        },
      });

    render(<ScannedProjectsPage onBack={() => {}} />);

    expect(await screen.findByRole("heading", { name: /Project Command Center/i })).toBeInTheDocument();
    expect(await screen.findByText(/Pretty Demo/i)).toBeInTheDocument();
    expect(await screen.findByRole("img", { name: /Pretty Demo thumbnail/i })).toHaveAttribute(
      "src",
      "http://127.0.0.1:8000/projects/1/thumbnail/image?v=%2Fold%2Fthumb.png"
    );
    expect(await screen.findByText(/Interactive dashboard for project analytics\./i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: /signals/i }));
    expect(await screen.findByText(/Detected Stack/i)).toBeInTheDocument();
    expect(screen.getByText(/Python/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: /contributors/i }));
    expect(await screen.findByRole("heading", { name: /Contributor Roles/i })).toBeInTheDocument();
    expect(await screen.findByText(/Confidence: 82%/i)).toBeInTheDocument();
    expect(await screen.findByText(/Team Composition: 1 Backend Developer/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: /activity/i }));
    expect(await screen.findByText(/Scan Activity/i)).toBeInTheDocument();
    expect(await screen.findByText(/Nightly scan/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/Search projects/i), {
      target: { value: "beta" },
    });

    expect(screen.getByRole("button", { name: /beta_project/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Pretty Demo/i })).not.toBeInTheDocument();
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
                    llm_summary: {
            text: "Original summary",
            updated_at: "2026-02-03T10:00:00Z",
          },
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
          llm_summary: {
  text: "Updated summary text",
  updated_at: "2026-02-04T10:00:00Z",
},
        },
      })
      .mockResolvedValueOnce({
        data: [{ id: 1, name: "demo_project", custom_name: "Updated Display Name" }],
      });

    axios.patch.mockResolvedValueOnce({ data: {} });

    render(<ScannedProjectsPage onBack={() => {}} />);

    expect(await screen.findByText(/demo_project/i)).toBeInTheDocument();

    const [editButton] = await screen.findAllByRole("button", { name: /Edit Project/i });
    fireEvent.click(editButton);

    fireEvent.change(screen.getByLabelText(/Display Name/i), {
      target: { value: "Updated Display Name" },
    });
    fireEvent.change(screen.getByLabelText(/Repo URL/i), {
      target: { value: "https://new-url.com" },
    });
    fireEvent.change(screen.getByLabelText(/Thumbnail Path/i), {
      target: { value: "/new/thumb.png" },
    });

    fireEvent.change(screen.getByLabelText(/LLM Summary/i), {
  target: { value: "Updated summary text" },
});

    fireEvent.click(screen.getByRole("button", { name: /Save Changes/i }));

    await waitFor(() => {
  expect(axios.patch).toHaveBeenCalledWith(
    expect.stringMatching(/\/projects\/1$/),
    {
      custom_name: "Updated Display Name",
      repo_url: "https://new-url.com",
      thumbnail_path: "/new/thumb.png",
      summary_text: "Updated summary text",
    }
  );
});

await waitFor(() => {
  expect(screen.getByText(/Updated summary text/i)).toBeInTheDocument();
});
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

    expect(
      await screen.findByText('Are you sure you want to delete "Pretty Project Name"?')
    ).toBeInTheDocument();

    expect(axios.delete).not.toHaveBeenCalled();
  });

test("renders evidence items with value, source, and url", async () => {
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
        },
        skills: [],
        languages: [],
        contributors: [],
        contributor_roles: { contributors: [], summary: {} },
        scans: [],
        files_summary: { total_files: 0, extensions: {} },
        evidence: [
          {
            id: 10,
            type: "metric",
            value: "10k+ downloads",
            source: "GitHub",
            url: "https://example.com",
          },
        ],
        llm_summary: null,
      },
    });

  render(<ScannedProjectsPage onBack={() => {}} />);

  fireEvent.click(await screen.findByRole("tab", { name: /evidence/i }));
  const evidenceSection = await screen.findByText(/Project Evidence/i);
  const evidenceContainer = evidenceSection.closest('article');

  expect(await within(evidenceContainer).findByText(/10k\+ downloads/i)).toBeInTheDocument();
  expect(within(evidenceContainer).getByText(/Source: GitHub/i)).toBeInTheDocument();
  expect(within(evidenceContainer).getByText(/Evidence URL: https:\/\/example\.com/i)).toBeInTheDocument();
  expect(within(evidenceContainer).queryByRole("link", { name: /view evidence/i })).not.toBeInTheDocument();
});

test("deletes evidence when delete button is clicked", async () => {
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
        },
        skills: [],
        languages: [],
        contributors: [],
        contributor_roles: { contributors: [], summary: {} },
        scans: [],
        files_summary: { total_files: 0, extensions: {} },
        evidence: [
          {
            id: 10,
            type: "metric",
            value: "10k+ downloads",
          },
        ],
        llm_summary: null,
      },
    });

  axios.delete.mockResolvedValueOnce({ data: {} });

  // refreshProjectData makes two GET calls after delete
  axios.get
    .mockResolvedValueOnce({
      data: {
        project: { id: 1, name: "demo_project", custom_name: null },
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

  render(<ScannedProjectsPage onBack={() => {}} />);

  fireEvent.click(await screen.findByRole("tab", { name: /evidence/i }));
  const evidenceSection = await screen.findByText(/Project Evidence/i);
  const evidenceContainer = evidenceSection.closest('article');

  const deleteButton = await within(evidenceContainer).findByRole("button", { name: /delete/i });
  fireEvent.click(deleteButton);
  fireEvent.click(await screen.findByRole("button", { name: /yes, delete evidence/i }));

  await waitFor(() => {
    expect(axios.delete).toHaveBeenCalledWith(
      expect.stringMatching(/\/projects\/1\/evidence\/10/)
    );
  });
});

test("renders formatted evidence type and plain evidence url text", async () => {
  axios.get.mockImplementation((url) => {
    if (url.includes("/projects/")) {
      return Promise.resolve({
        data: {
          project: { id: 1 },
          evidence: [
            {
              id: 1,
              type: "external_link",
              value: "10k downloads",
              url: "https://example.com"
            }
          ]
        },
      });
    }

    return Promise.resolve({
      data: [{ id: 1, custom_name: "Test Project" }],
    });
  });

  render(<ScannedProjectsPage onBack={() => {}} />);

  fireEvent.click(await screen.findByRole("tab", { name: /evidence/i }));
  const evidenceSection = await screen.findByText(/Project Evidence/i);
  const evidenceContainer = evidenceSection.closest('article');

  expect(
    within(evidenceContainer).getByText((content, element) =>
      element.tagName.toLowerCase() === "span" && /external link/i.test(content)
    )
  ).toBeInTheDocument();
  expect(await within(evidenceContainer).findByText(/10k downloads/i)).toBeInTheDocument();
  expect(within(evidenceContainer).getByText(/Evidence URL: https:\/\/example\.com/i)).toBeInTheDocument();
  expect(within(evidenceContainer).queryByRole("link", { name: /view evidence/i })).not.toBeInTheDocument();
});

test("renders evidence delete button when detail payload includes evidence id", async () => {
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
        },
        skills: [],
        languages: [],
        contributors: [],
        contributor_roles: { contributors: [], summary: {} },
        scans: [],
        files_summary: { total_files: 0, extensions: {} },
        evidence: [
          {
            id: 10,
            type: "metric",
            value: "10k+ downloads",
          },
        ],
        llm_summary: null,
      },
    });

  render(<ScannedProjectsPage onBack={() => {}} />);

  fireEvent.click(await screen.findByRole("tab", { name: /evidence/i }));
  const evidenceSection = await screen.findByText(/Project Evidence/i);
  const evidenceContainer = evidenceSection.closest("article");

  expect(await within(evidenceContainer).findByRole("button", { name: /delete/i })).toBeInTheDocument();
});

test("newly added evidence is immediately deletable from local state", async () => {
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

  axios.post.mockResolvedValueOnce({
    data: {
      evidence_id: 77,
      message: "Evidence added successfully",
    },
  });

  axios.delete.mockResolvedValueOnce({ data: {} });
  axios.get
    .mockResolvedValueOnce({
      data: {
        project: {
          id: 1,
          name: "demo_project",
          custom_name: null,
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

  render(<ScannedProjectsPage onBack={() => {}} />);

  fireEvent.click(await screen.findByRole("tab", { name: /evidence/i }));
  fireEvent.change(screen.getByLabelText(/Outcome \/ Impact/i), {
    target: { value: "10k+ downloads" },
  });
  fireEvent.change(screen.getByLabelText(/URL/i), {
    target: { value: "https://example.com" },
  });
  fireEvent.click(screen.getByRole("button", { name: /add evidence/i }));

  const evidenceSection = await screen.findByText(/Project Evidence/i);
  const evidenceContainer = evidenceSection.closest("article");
  const deleteButton = await within(evidenceContainer).findByRole("button", { name: /delete/i });
  expect(deleteButton).toBeEnabled();

  fireEvent.click(deleteButton);
  fireEvent.click(await screen.findByRole("button", { name: /yes, delete evidence/i }));

  await waitFor(() => {
    expect(axios.delete).toHaveBeenCalledWith(
      expect.stringMatching(/\/projects\/1\/evidence\/77/)
    );
  });
});

test("evidence delete button opens in-app confirmation modal", async () => {
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
        },
        skills: [],
        languages: [],
        contributors: [],
        contributor_roles: { contributors: [], summary: {} },
        scans: [],
        files_summary: { total_files: 0, extensions: {} },
        evidence: [
          {
            id: 10,
            type: "metric",
            value: "10k+ downloads",
          },
        ],
        llm_summary: null,
      },
    });

  render(<ScannedProjectsPage onBack={() => {}} />);

  fireEvent.click(await screen.findByRole("tab", { name: /evidence/i }));
  const evidenceSection = await screen.findByText(/Project Evidence/i);
  const evidenceContainer = evidenceSection.closest("article");

  fireEvent.click(await within(evidenceContainer).findByRole("button", { name: /delete/i }));

  expect(await screen.findByText(/Are you sure you want to delete this evidence item/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /yes, delete evidence/i })).toBeInTheDocument();
});
});
