const primaryNavigation = [
  {
    label: "Now",
    active: true,
  },
  {
    label: "Plan",
    active: false,
  },
  {
    label: "Knowledge",
    active: false,
  },
  {
    label: "Focus",
    active: false,
  },
];

const contextualNavigation = [
  "Goals",
  "Initiatives",
  "Epics",
  "Stories",
  "Work Cycles",
  "Work Packets",
  "Requirements",
  "Specifications",
  "ADRs",
];

export function Navigator() {
  return (
    <aside className="navigator">
      <div className="navigator-section">
        <p className="section-label">Workspace</p>

        <nav className="primary-navigation" aria-label="Workbench">
          {primaryNavigation.map((item) => (
            <button
              className={item.active ? "nav-item active" : "nav-item"}
              key={item.label}
              type="button"
            >
              <span className="nav-indicator" />
              {item.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="navigator-section">
        <p className="section-label">Explore</p>

        <div className="context-navigation">
          {contextualNavigation.map((item) => (
            <button className="context-item" key={item} type="button">
              {item}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
