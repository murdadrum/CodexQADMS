import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ConsolePanel } from "./console-panel";

const RECENT_RUNS_KEY = "qadms.console.recent_runs.v1";
const FILTER_PRESETS_KEY = "qadms.console.filter_presets.v1";
const FILTER_STATE_KEY = "qadms.console.filter_state.v1";

describe("ConsolePanel persistence", () => {
  beforeEach(() => {
    window.localStorage.clear();
    Object.defineProperty(global, "fetch", {
      writable: true,
      value: jest.fn().mockRejectedValue(new Error("network unavailable")),
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("loads recent run in detail drawer before applying to form", async () => {
    const run = {
      id: "run-1",
      sourceId: "source-history",
      timestamp: "2026-02-09T12:00:00.000Z",
      apiBase: "http://127.0.0.1:9000",
      tokenSource: "figma_export",
      validationValid: true,
      totalViolations: 2,
      payloadText: "{\"colors\":[]}",
    };
    window.localStorage.setItem(RECENT_RUNS_KEY, JSON.stringify([run]));

    const user = userEvent.setup();
    render(<ConsolePanel />);

    await user.click(screen.getByRole("button", { name: "Details" }));
    expect(screen.getByText("Run Detail")).toBeInTheDocument();
    expect(screen.getByText("source-history")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Load This Run" }));
    expect(screen.getByLabelText("Source ID")).toHaveValue("source-history");
    expect(screen.getByText(/Loaded recent run from/i)).toBeInTheDocument();
  });

  it("persists recent runs after import fallback", async () => {
    const user = userEvent.setup();
    render(<ConsolePanel />);

    await user.click(screen.getByRole("button", { name: "Import Tokens" }));

    await waitFor(() => {
      expect(screen.getByText(/API unavailable\./i)).toBeInTheDocument();
    });

    const stored = JSON.parse(window.localStorage.getItem(RECENT_RUNS_KEY) || "[]");
    expect(stored.length).toBe(1);
    expect(stored[0].sourceId).toBe("source-theme");
  });

  it("saves and reapplies filter presets from local storage", async () => {
    const user = userEvent.setup();
    render(<ConsolePanel />);

    await user.click(screen.getByRole("button", { name: "Import Tokens" }));

    const searchInput = await screen.findByPlaceholderText("title, code, token path...");
    await user.type(searchInput, "contrast");

    await user.type(screen.getByPlaceholderText("Preset name"), "ContrastOnly");
    await user.click(screen.getByRole("button", { name: "Save Preset" }));

    const presets = JSON.parse(window.localStorage.getItem(FILTER_PRESETS_KEY) || "[]");
    expect(presets.length).toBe(1);
    expect(presets[0].name).toBe("ContrastOnly");

    await user.clear(searchInput);
    expect(searchInput).toHaveValue("");

    await user.click(screen.getByRole("button", { name: "ContrastOnly" }));
    expect(searchInput).toHaveValue("contrast");

    const filterState = JSON.parse(window.localStorage.getItem(FILTER_STATE_KEY) || "{}");
    expect(filterState.search).toBe("contrast");
  });
});
