import { DigitalClock } from "../components/DigitalClock";
import { ClockCard } from "../components/ClockCard";
import { StopSection } from "../components/StopSection";
import { StatusPanel } from "../components/StatusPanel";
import { useStatus } from "../lib";

export function HomePage() {
  const { data: status, isLoading, error } = useStatus();

  if (isLoading) {
    return <div className="loading">Connecting to Kalembang...</div>;
  }

  if (error) {
    return (
      <div className="error-message">Failed to connect to Kalembang API</div>
    );
  }

  return (
    <>
      {/* Digital Clock */}
      <DigitalClock />

      {/* Clock 1 */}
      <ClockCard
        clockId={1}
        title="Clock 1"
        enabled={status?.clock1.enabled ?? false}
        duty={status?.clock1.duty ?? 100}
      />

      {/* Clock 2 */}
      <ClockCard
        clockId={2}
        title="Clock 2"
        enabled={status?.clock2.enabled ?? false}
        duty={status?.clock2.duty ?? 100}
      />

      {/* Stop Section */}
      <StopSection />

      {/* Status Panel */}
      <StatusPanel status={status ?? null} />
    </>
  );
}
