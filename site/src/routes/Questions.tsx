/**
 * `/questions` — what is blocked on Andre.
 *
 * Ordered by what each one unblocks, not by how easy it is to answer.
 */
import { CircleCheck } from "lucide-react";
import { DataTable, Td, Tr } from "../design/DataGrid";
import { EmptyState, ErrorState, Page, PageHeader, Section } from "../design/primitives";
import { getQuestions } from "../lib/data";
import { useAsync } from "../lib/useAsync";

const ORDER = { blocking: 0, soon: 1, nice: 2 } as const;
const LABEL = { blocking: "blocking", soon: "needed soon", nice: "nice to have" } as const;
const TONE = {
  blocking: "text-critical",
  soon: "text-caution",
  nice: "text-subtle",
} as const;

export function Questions() {
  const state = useAsync(getQuestions, []);
  if (state.status === "loading") return <Page>{null}</Page>;
  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Questions" />
        <ErrorState title="Could not load open questions">{state.error.message}</ErrorState>
      </Page>
    );
  }
  const rows = [...state.data].sort((a, b) => ORDER[a.priority] - ORDER[b.priority]);

  return (
    <Page>
      <PageHeader
        title="Questions"
        lede="Open questions for Andre, ordered by what each one unblocks. Nothing here gets guessed."
      />
      <Section>
        {rows.length === 0 ? (
          <EmptyState icon={CircleCheck} title="Nothing is blocked on you">
            Every open question has been answered.
          </EmptyState>
        ) : (
          <DataTable head={["Priority", "Question", "What it unblocks"]}>
            {rows.map((q) => (
              <Tr key={q.id}>
                <Td className={`whitespace-nowrap text-micro uppercase tracking-wide ${TONE[q.priority]}`}>
                  {LABEL[q.priority]}
                </Td>
                <Td>{q.question}</Td>
                <Td className="text-small text-muted">{q.unblocks ?? q.section}</Td>
              </Tr>
            ))}
          </DataTable>
        )}
      </Section>
    </Page>
  );
}
