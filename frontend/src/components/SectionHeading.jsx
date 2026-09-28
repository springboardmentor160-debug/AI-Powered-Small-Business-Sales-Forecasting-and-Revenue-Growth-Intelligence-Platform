export default function SectionHeading({ eyebrow, title, action }) {
  return (
    <div className="section-heading">
      <div>
        <p className="section-heading__eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
      </div>
      {action ? <span className="section-heading__action">{action}</span> : null}
    </div>
  );
}
