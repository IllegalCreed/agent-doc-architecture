# Make the Agent Read Only What It Should: Documentation Routing (2)

*This post is an English translation of the Chinese original: [让 Agent 只读该读的——文档路由设计（二）](../02-routing.md).*

> This is the second post in the series "Agent-first Documentation Layers for Large Projects." [Post 1](01-agent-is-not-amnesiac.md) gave the four-layer model, L0–L3: L0 is the entry file loaded automatically every session, L1 is the specs split by work type, L2 is module and change documents, and L3 is execution evidence. This post answers one question: the agent is handed a task — which documents should it read? The material is still the enterprise payment-approval system.

## 1. The spec was already there. There was just no road.

Post 1 opened with that release seal (freeze the version, run the full test suite, tag, and produce the package). On September 16 two versions were tagged on the same day, and neither changelog nor handover note existed until the rule-making commit two days later. That same commit created the release-seal spec and added an "operation → required reading" table to the entry file. This post digs down from that table.

First, say "could not find it" precisely. Post 1 already noted that before the rule was written, the definition of the "six-suite full run" was already in the project testing spec, and a search of the entry file of that day for "full suite" and "release seal" came back empty.

Two failures have to be distinguished. Their fixes are completely different.

- **Buried.** The road is there. A few hundred lines of narrative cover it. The fix is to shorten, to bold, to move it somewhere visible.
- **Unreachable.** Starting from the task in hand, the entry has no signpost pointing at it. There is only one fix: build a road.

Ours was the second, and it was more hidden than "there is no reference." Strictly speaking, the reference graph had a two-hop path. The development-workflow section of the entry file pointed its "detailed spec" at the development-workflow document (the project's development spec). That document's related-docs table had a row linking to the project testing spec, and the cell said "five-layer test pyramid." The full-suite definition was on line 154 of that spec. The path was connected. For an agent that had been handed a release seal, no signpost along the way said "full suite" or "release seal." Another path mentioned the release seal and then ended in the wrong place. The entry mentioned the path of the change index. Three rows in the index, "v2.0.x local release seal and packaging," linked to those seals' own documents. One of the requirements listed the six suites item by item. That was one historical instance, not the current definition, and it did not link to the testing spec. For a reader with no memory across sessions, a document that cannot be reached from the task in hand does not exist, however well it is written.

How the rule-making commit built the road is worth a close look. It did not copy the six-suite definition into the entry file. It added a table, and the first row pointed "release seal / produce a package / tag / say 'full suite green'" at the new release-seal spec. The entry file went from 410 lines to 424. The new section, title and introduction included, was 14 lines. The 7 rows of the table were 7 roads, and the release-seal road took one of them.

After that, the versions can be checked one by one. As of October 14, the nine versions published after the rule, v2.0.5 through v2.3.1, each have both a changelog and a handover note. Release-seal test reports exist for every version from v2.1.0 on (v2.0.5 has none). I do not credit a table alone — the same commit also wrote the release-seal checklist and the required contents of the two release documents. For any of that to work, it has to be read, and what connected it to the entry was that one row of the routing table.

So the question of this post is not "how do we make the agent remember the spec." It is: **how do we guarantee a road from the entry to every spec that should be read, and that the agent walks only the roads it should.**

## 2. Three shapes of routing failure

Widen the view from that one release seal to the whole doc system. Routing fails in three shapes, and all three showed up in our project.

1. **No road.** The spec exists and cannot be reached from the entry. That is the opening.
2. **The road is too wide.** The entry file loads the detailed rules of every kind of work. Every session has to swallow all of it, and the one line that matters is diluted. This is the L0 swelling from post 1.
3. **The road breaks halfway.** The routing table delivers the agent to the project-layer spec, and the project layer never says which shared spec it inherits. The agent finishes the project layer and thinks it has read everything. Section 10 goes into this.

The three shapes have one root cause: **the docs are organized the way the writer classifies them, while the agent arrives holding only one question — what am I supposed to do now.** Writers organize by directory, by document type, by time. That is natural for someone who knows the repo. The agent is a newcomer every session. It does not know what the repo looks like. It only knows the user told it to seal a release, change a table, or review a diff. The key of the route has to be something the agent already holds when it walks in.

## 3. Three principles

**Principle 1: the entry file only routes. It does not carry content.** (Answers "context is limited and it costs money.") Post 1 derived the same sentence from "no memory across sessions": the entry is the one thing the agent is certain to read, so it has to exist. Here is the other half. The entry file is loaded in full on every session. Every line that is put into it is paid for by every session. Copy the six-suite definition into the entry, and every session that has nothing to do with a release seal reads it once. Make it a route, and only the release-seal session pays that cost.

**Principle 2: route by work type, not by directory.** (Answers "no memory across sessions.") A directory tree answers "where is the thing," on the premise that the reader knows what the thing is called and which class it belongs to. That premise is itself memory. The agent has no such memory when it walks in. It has only the task the user handed it. The two-hop reference in the opening is the counterexample: the directories and the references were connected, but the signposts were written as "here is what we have," not as "here is what you are doing." So the first column of the routing table is an action: seal a release, change a table structure, review code. It is not a directory name.

**Principle 3: every hop declares the next hop and its own parent.** (Answers "follows the literal text and does not infer intent.") A human who reads a "project database spec" naturally thinks "there is probably a shared one too." An agent does not. If a document does not say "I am a subset of that one," the agent treats it as the whole rule. If it does not say "where to go after reading," the agent stops. Routing is not only the entry's job. Every document along the road has to answer both questions.

## 4. Mechanism 1: the "operation → required reading" table

The fragment below is arranged in the recommended shape. The source is the table now in our project's entry file, redacted and excerpted. The original table had only two columns, with the point written in a parenthetical. Here the point is its own column.

```markdown
| Operation | Required spec | One-sentence point |
|---|---|---|
| Release seal / produce a package / tag / say "full suite green" | handbook/engineering/release-process.md | "Full suite green" is allowed only when all six suites pass by the defined criteria |
| DB schema / cross-environment data change | handbook/database/project-database-changes.md | A schema change requires an incremental script; the script must run on the production executor |
| Write / change / review any test | testing/guides/project-testing.md | Pick the layer from the "work type → test layer" table first; do not escalate a UI contract to end-to-end |
| Verify frontend behavior in a browser | The "do not guess selectors" section of the entry file | Browser automation is for locating, and is not acceptance evidence |
| Code review / re-review | The change's handoff.md + test-cases.md | The conclusion must carry "path:line" evidence |
| Change the workflow engine | tracks/refactor/roadmap.md + the current change | Read the historical lessons before changing engine behavior |
| Change the mobile client | The "hard constraints for real-device compatibility" section of the entry file | Check a new dependency against the WebView version floor first |

**Layered reading:** L0 = the hard rules at the top of the entry file, always in force. L1 = the table above, addressed by work type; before starting, read only the document in the matching row. L2 = the module's change plan and handoff; read them when entering that module. Do not read the whole repo for one task, and do not start from memory without reading L1.
```

This table is where principle 2 lands (answers "no memory across sessions"): a newcomer can look up the next hop from the task already in hand. Two things are worth unfolding: what gets a row, and the third column.

**The bar for a row: high risk, low frequency, easy to get wrong from memory.**

- High risk: getting it wrong is expensive or irreversible. Production databases, releases, cross-environment data.
- Low frequency: something done once or twice a month. The relevant spec will not happen to be sitting in recent context.
- Easy to get wrong from memory: the agent's common sense produces an answer that looks reasonable and is wrong. "Full suite" is the type case. In common sense, full means "run all the tests." In the project, the definition is a fixed six suites, and none may be omitted.

Ordinary coding does not get a row. "Write a list page" has no row. It meets none of the three bars. Rules for high-frequency work belong in the development spec, and one link from the entry to that spec is enough. The moment the table starts collecting ordinary operations, it grows into a second development spec.

**The "one-sentence point" column delivers the most important constraint even if the hop is never taken.** The routing table is in L0, so it is read every time. The target document is in L1, one hop further. The agent may skip the hop because context is tight, or because it judges "this change is small." The point column is the floor: even without the hop, "a schema change requires an incremental script" is already in front of it. There is a side effect. If a spec's point cannot be written as one sentence, the spec itself often has no core rule, and the target document should be cleaned up first.

The layered-reading paragraph under the table blocks both directions. "Do not read the whole repo for one task" prevents reading too much. "Do not start from memory without reading L1" prevents reading too little. It is the model from post 1, written as one paragraph inside L0, so the agent knows which layer it is on every time it walks in.

Look again at the point on the code-review row: the conclusion must carry "path:line" evidence. A review conclusion is ultimately for a human to adjudicate, so the routing table does not only say what the agent reads. It also says what shape the evidence handed to the adjudicator must have. Also, two rows name "some section of the entry file" as the required reading. That is a signal. Section 10 comes back to it.

## 5. Mechanism 2: one entry for every agent

On March 4 the entry file was 128 lines. By August 20 it had grown to 406, and the name had always been CLAUDE.md, the filename Claude Code expects. Codex and Kimi were also in the collaboration. An entry named for one tool's convention is not necessarily loaded when the tool changes. The documentation reshuffle on September 3 gathered the rules into AGENTS.md, and CLAUDE.md shrank to a forwarder. It is 5 lines now, and it says three things. The skeleton, paraphrased:

```markdown
# Compatibility entry for <tool name>

The only project rules are in AGENTS.md. Read it in full before starting.
Do not repeat any rule in this file. To add or change a rule, edit AGENTS.md,
so every agent uses the same source of truth.
```

The forwarder may not contain a single rule. The moment it has one, the two entries grow apart, and different agents see different project rules.

The single entry has another half: **personal memory.** Some agent tools keep a memory file on the machine for the user and load it across sessions. It is not in the repo. Other agents, and other machines, cannot see it. The batch of project-level lessons in symptom 6 of post 1 was stuck there.

To decide where an experience goes, ask one question: **if the agent changes, or the machine changes, should this still be in force?** (Answers "several agents at once.") If yes, it goes into the repo, placed in the entry or in an L1 spec according to its layer. If no, it stays in personal memory. What stays should be only collaboration preferences: reply in Chinese, show the human the diff before committing.

## 6. Mechanism 3: shared → project, two layers of inheritance

L1 specs come in two layers. The **shared layer** writes rules that hold across projects, and it leaves **placeholders**: the blanks each project has to answer for itself. Which database dialect, where migration scripts live, which suites the full run includes. The **project layer** writes only four things: the filled placeholders, this project's current state, exceptions to the shared rules, and the pitfalls this project has hit.

The two layers are joined by one inheritance declaration, and that declaration has to sit at the top of the project layer. The reason is routing. The routing table points at the project layer, because that is where the directly executable rules are, so the agent lands on the project layer. If the project layer does not name its parent, the shared layer is unreachable from it — the same shape as the opening, happening inside L1. (Answers "follows the literal text and does not infer intent.")

The positive example is the testing landing note of our mobile subproject. The first sentence under the title is the inheritance declaration (the link has been replaced with the document name):

> This document is the in-project filling of the Shared Testing Spec (§10). Shared content is not repeated. It fills only this project's placeholders, current state, and exceptions. Living document: when execution hits a new pitfall, write it back here.

One sentence answers three questions: who the parent is; what this document writes and what it does not; that this document will be updated. The parent has the matching interface. Section 10 of the shared testing spec, "Landing and exceptions," lists the blanks in a "placeholder | the project must specify" table. The placement rules in the testing-center README add one more constraint: a subproject may have its own landing note, "but it must be reachable from this page, and it must not copy the shared spec into a second source of truth."

The skeleton of a project layer:

```markdown
# Database change spec (project layer)

> Inherits: <shared database change spec>. This document writes only filled
> placeholders, current state, exceptions, and this project's pitfalls.
> Whatever is not written here follows the shared layer. Where this document
> conflicts with the shared layer, the "Exceptions" section of this document wins.

## Filled placeholders
## Current state
## Exceptions
## This project's pitfalls
```

"Who wins on a conflict" has to be written down. When the two layers disagree, an agent that follows the literal text will not guess the author's intent. It will pick one of the two sentences and believe it. Our own counterexample is in section 10.

## 7. Mechanism 4: a hop-by-hop routing chain

The routing table solves only the first hop. From the entry to the body, our design is a chain, and each layer answers only "where next":

**Entry file → docs home (by responsibility) → top-level directory README (second-level routing + placement rules) → the AI Quick Path at the top of the document → the body**

- The **docs home** splits by responsibility. The opening paragraph of ours says "when looking something up, first judge the document's responsibility; stop guessing a location from the filename in the root," and the "quick entry" table under it has only two columns: what you want to know | the entry.
- A **top-level directory README** does second-level routing and also writes the placement rules. The testing center's README has only two sections. "Navigation" tells the reading agent which document to open. "Placement rules" tell the writing agent where new content goes. Reading and writing walk the same map, so a new document cannot step around the route. (Placement rules are the subject of post 3.)
- The **AI Quick Path** is an ordered reading list at the top of a document: for this kind of task, read this section of the document first, then that document. It is the last hop of the chain. It takes the agent from the door of the document straight to the section it needs.

```markdown
## AI Quick Path

For this kind of task, read in order:
1. The "core rules" section of this document.
2. <the parent shared spec>: rules this document does not cover.
3. <the related change's requirements and design>: why it changed, and what changed.
4. <the matching index>: take a number, look up history.
```

Why a chain, and not one big table? (Answers "context is limited and it costs money.") Each layer carries only the next hop, so each step the agent takes costs a small piece of tokens. Adding a document changes only the README of the directory it lives in. The entry file is not touched, and the routing table does not grow as the docs grow.

The last hop is the one we did least of. Before the cleanup, only 2 documents under the docs tree had an AI Quick Path. The earlier layers of the chain were there. The last hop was mostly absent, and the agent still had to start from the top once it reached the door of the document.

## 8. Mechanism 5: a handoff document is a one-time route

The routing table serves every session. A handoff document (handoff.md) serves one: a change passing from this agent to the next. In one of our cross-layer handoffs, the section "task notes for the coding agent" opens with the reading order:

> Read this directory's requirements, design, implementation, test-cases, and impact-map first, then the root AGENTS.md and the development workflow.

"This directory" means the change's bundle: one change's requirements, design, implementation record, and test cases in a single directory. A later section is called "what every review handoff must include," and it lists 5 items: the branch, the commits, and the deviation from the plan; the IDs of new cases, the actual commands, the results, and where the report is; the key evidence for this stage; when a migration is involved, the number-collision check plus first-run and re-run evidence; and an update to the actual execution record. After that is a "review block list." Each check states "the concrete condition that fails it," for the agent responsible for the review.

This is a route customized for this change and this successor. It points two ways (answers "no memory across sessions": the agent taking over does not know where the previous session stopped):

- **In:** what to read first, and in what order. Same shape as the routing table, scoped down to one bundle.
- **Out:** which evidence every review handoff must attach. It specifies the shape of what the agent hands to the next link.

The review block list and the routing table connect. The "code review" row of the routing table points exactly at it. The full path of a review task is therefore: entry routing table → that change's handoff → the block list and the case matrix → the code. The human is at the end of the chain, reads the evidence the agent arranged against the list, and releases or sends it back.

A handoff document is one-time. When the change is finished, it becomes L2 history and no longer carries a routing duty.

## 9. How each kind of work walks

Put the five mechanisms together and list the full path by work type. The table below is the recommended shape, not a copy of our project's current state. The current state is still some distance from it; see the next section. The "project layer" column says what the project layer has to fill in.

| Work type | L1 entry | Shared layer | Project layer | Next hop | Human's role |
|---|---|---|---|---|---|
| Requirements | Documentation-model spec | Requirements template and required sections | ID and directory conventions | The change bundle's requirements document | Make the call on scope |
| Development | Project development spec | Shared development spec | Branch model, this project's hard rules | The change's design and handoff | Approve the plan |
| Refactoring | Project development spec | Shared development spec | Historical lessons of the refactoring track | The current change bundle | Make the call on track priority and on closing it |
| Testing | Project testing spec | Shared testing spec | Filled placeholders, subproject landing notes | Case index, the change's cases | Make the call on the testing definition |
| Release seal | Release-seal spec | Shared release process | Full-suite definition, release-seal checklist | The two release documents (write them); L3 release-seal test report | Accept the release seal: release against the checklist |
| User manual | Manual-maintenance convention | — | Which changes must update the manual | The matching manual section (write only; not a source of knowledge) | Spot-check, then confirm the deliverable |
| DB change | Project database spec | Shared database change spec | Dialect, migration directory, execution tool, pitfalls | Migration index (take a number) | Make the call on compatibility rules and exceptions |
| Deploy | Deployment runbook | Shared deployment spec | Per-environment booklets, package-name rules | This deploy's migration execution list | Approve production |
| Code review | Review checks | Shared review list | This project's checks | The handoff's block list and case matrix | Release or send back on the evidence |
| Browser debugging | Browser-debugging convention | — | Selector convention | Frozen into a test case | Accept: release on the result of the frozen case |

Look at "next hop" first. No cell points back at the entry file. The route only goes downward, and it ends at L2, L3, a deliverable, or the code itself. Cells marked "write" are deliverables. The agent maintains them and does not learn the job from them. The "shared layer" has empty cells, because not every kind of work needs to be split in two. Split only when the rule can be reused across projects. Every cell of "human's role" is a decision point. What the human reads while deciding is exactly the report, the evidence, and the execution list produced by the "next hop" column.

## 10. How routing breaks

### Failure 1: the routing table grows into the entry file itself

Two rows in the fragment of mechanism 1 name "some section of the entry file" as the required reading. The original table was clearer: of the 7 rows at the time the rule was written, 3 pointed back at the entry file itself. On October 14 it grew to 12 rows, and the ones pointing back at itself became 5. The layered-reading principle under the table lists four L0 hard rules of its own, and only two of those 5 rows point at them. The other 3 — the checklist for syncing a new business type, the selector convention, and real-device compatibility for the mobile client — are details that only a specific kind of work needs, and they live in an entry file that is loaded every time.

Another sign is inside the cells. The original table wrote its points in parentheticals. The parenthetical in the browser cell contained the rule text, the evidence standard, and the date the rule was codified. A cell had grown into a paragraph, and the routing table had started to carry content.

Meanwhile the entry file grew from 424 lines after the rule was written to 457 (after the cleanup it fell to 242; see post 4). The routing table was supposed to take weight off the entry file. Written this way, it makes the file thicker.

Three counters:

- If a row's target is "some section of the entry file," first ask whether it is on the L0 hard-rule list. If it is not, sink that section into an L1 document and point the route at it.
- The point column is allowed one sentence. Whatever does not fit belongs in the target document.
- Before adding a row, pass it through the bar: high risk, low frequency, easy to get wrong from memory.

### Failure 2: pointing at a document that has been superseded

A broken link at least shows itself: the agent opens it and gets an error. Our entry layer currently has 0 broken links. The real danger is a link that is alive and a target that is no longer current fact. An agent that follows the literal text arrives and believes. "Superseded" has two forms. One is formally replaced by a new version. The other was only ever one historical instance, and it got used as the current definition.

Our release-seal route had the second form, at the end of the chain. The release-seal spec at the time the rule was written said, of the handover note, "the template is to follow v2.0.2-delivery.md," followed by a list of required items. The last hop of the routing chain landed on a historical delivery document, not on a current definition. The second two-hop path in the opening has the same shape: the signpost mentioned the release seal, and the destination was the requirements of one particular seal. Pointing at a historical instance writes "do it the way we did last time" into the rules. Our handover notes then drifted generation by generation. From v2.0.3 on, they were missing the SHA-256 checksum the spec explicitly required. How to do templates is covered in post 3.

The first form is a field problem. A document is replaced by a new version, and the header never writes `Replaced by`. Post 1 counted this: most of our bundles did not write the field, so the rule "if you read a superseded document, jump first" spun in place.

The counter: a route points only at "current definition" documents (specs, templates, indexes), or it is written as a pointer that changes with the task, such as "the handoff of the corresponding change." It does not hard-code one instance (some version's delivery document, some historical change plan). A target that can be superseded must carry `Replaced by`. A script can check "the link is alive." It cannot check "the target is still in force." The latter depends on the metadata field. How to enforce it is left to post 4.

### Failure 3: the project layer does not declare what it inherits

This is the most complete counterexample in our project. Before the cleanup, the project testing spec and the project database spec each cited their shared spec 0 times. The shared database spec was still marked draft v0.1. At the time, the only project-layer document that correctly declared its inheritance was the mobile testing landing note from mechanism 3.

The irony is that the shared database spec already had an AI Quick Path at the top: step 1, read the shared spec; step 2, read the project adaptation. The parent pointed at the child. The road only ran downward. The routing table delivered the agent straight to the project layer, and the project layer had not one sentence sending it one level up. An agent that came in along the routing table finished the project database spec, and the shared layer's rules did not exist for it. The two layers had become two documents that did not know each other.

The counter: the inheritance declaration at the top of the project layer is required, and it is the easiest thing for a machine to check (answers "can grep, glob, and run scripts"). The defect itself was found with one grep: whether a project-layer document contains a link to the shared layer is one command. If the shared layer is still a draft, the project layer either pushes it to a final version or declares "this document is self-contained." Do not leave the agent to guess whether a draft counts. During the cleanup both project-layer specs gained an inheritance declaration at the top, the shared database spec was finalized, and a missing inheritance declaration is an error from doc-lint (see post 4).

## 11. Summary

1. A routing failure is often not "buried." It is "no road." A document that cannot be reached from the task in hand does not exist for the agent. A connected reference is not a road. Building the road beats bolding the text: the road in the opening takes one row of the entry.
2. Three principles. The entry file only routes and does not carry content (context is limited and it costs money). Route by work type, not by directory (no memory across sessions). Every hop declares the next hop and its own parent (follows the literal text and does not infer intent).
3. The routing table collects only operations that are high risk, low frequency, and easy to get wrong from memory. The one-sentence point delivers the most important constraint even if the hop is never taken.
4. One entry, and the rest forward. If an experience should still be in force under a different agent, it goes into the repo. It does not stay in personal memory.
5. Routing is a chain: entry → docs home → directory README → AI Quick Path → body. A handoff document is a one-time route for the next agent. It breaks in three places: the table grows into the entry, the end of the chain points at history, and the project layer does not acknowledge its parent.

### Series

1. [Agents Aren't Amnesiac — They Can't Find the Entry Point: Documentation Layers for Large Projects (1)](01-agent-is-not-amnesiac.md)
2. Make the Agent Read Only What It Should: Documentation Routing (2) (this post)
3. [Give Every Document Exactly One Place: Documentation Addressing (3)](03-addressing.md)
4. [Keep Documents from Rotting: The Document Lifecycle in the Agent Era (4)](04-lifecycle.md)
