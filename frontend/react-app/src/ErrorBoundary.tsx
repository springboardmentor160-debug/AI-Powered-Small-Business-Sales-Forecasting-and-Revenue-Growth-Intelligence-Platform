import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

interface Props { children: ReactNode; resetKey?: string }
interface State { failed: boolean }

/** One broken screen never blanks the whole app: show a calm message and a retry. */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { failed: false };

  static getDerivedStateFromError(): State { return { failed: true }; }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("UI error caught by boundary:", error, info.componentStack);
  }

  componentDidUpdate(prev: Props) {
    if (this.state.failed && prev.resetKey !== this.props.resetKey) this.setState({ failed: false });
  }

  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <div className="lx-fail" role="alert">
        <AlertTriangle size={28} />
        <h3>This section hit a problem</h3>
        <p>The rest of the platform is still working. You can try again or open another page.</p>
        <button type="button" className="button button-primary" onClick={() => this.setState({ failed: false })}>
          <RotateCcw size={16} /> Try again
        </button>
      </div>
    );
  }
}
