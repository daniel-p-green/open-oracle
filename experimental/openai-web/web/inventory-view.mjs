import {
  loadContestInventory,
  officeFamily,
  INVENTORY_VERSION,
} from "./office-source.mjs";
import { mountReadingGuide, mountSourceCheck } from "./reading-guide.mjs";

// Presentation state only. Session, cancellation, speech and evidence admission
// remain owned by the application; this component cannot start paid work.
const el = (tag, text) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  return node;
};
const link = (url, label) => {
  const node = el("a", label);
  node.href = url;
  node.target = "_blank";
  node.rel = "noopener noreferrer";
  node.className = "source-link";
  return node;
};
const button = (host, label, action) => {
  const node = el("button", label);
  node.type = "button";
  node.onclick = action;
  host.append(node);
  return node;
};

export async function mountContestInventory(
  host,
  {
    language,
    signal,
    isCurrent,
    onRead,
    readContext,
    onOffice,
    onMeasure,
    onActions,
    translationNote,
  },
) {
  const anchor = el("section");
  const text = (en, es) => (language === "es" ? es : en);
  host.replaceChildren(anchor);
  anchor.append(
    el(
      "p",
      text(
        "Checking retained official notice inventory…",
        "Consultando el inventario de avisos oficiales guardados…",
      ),
    ),
  );
  try {
    const value = await loadContestInventory(
      AbortSignal.any([AbortSignal.timeout(5000), signal]),
    );
    if (!anchor.isConnected) return;
    if (!isCurrent()) {
      anchor.textContent = text(
        "Inventory loading stopped. Choose the topic again to reload.",
        "Se detuvo la carga. Elija el tema de nuevo para cargarlo.",
      );
      return;
    }
    anchor.replaceChildren(
      el("h3", text("Browse public notices", "Explorar avisos públicos")),
    );
    anchor.append(
      el(
        "p",
        text(
          "55 printed contests · 34 candidate elections · 11 judicial retentions · 10 measures. Counts describe these retained documents, not your ballot or final write-in eligibility.",
          "55 concursos impresos · 34 elecciones de candidatos · 11 retenciones judiciales · 10 medidas. Son cifras de estos documentos guardados, no de su boleta ni de la elegibilidad final de candidatos por escrito.",
        ),
      ),
    );
    const authorityLabel = el(
      "label",
      text("Public source to browse", "Fuente pública que desea consultar"),
    );
    const authority = el("select");
    authority.id = "inventory-authority";
    for (const [id, label] of [
      ["all", text("Both notices · union", "Ambos avisos · conjunto")],
      ["kceb", "KCEB · Kansas City"],
      [
        "jceb",
        text("JCEB · outside Kansas City", "JCEB · fuera de Kansas City"),
      ],
    ]) {
      const option = el("option", label);
      option.value = id;
      authority.append(option);
    }
    authorityLabel.append(authority);
    const contestLabel = el(
      "label",
      text(
        "Choose a printed contest · original English title",
        "Elija un concurso impreso · título original en inglés",
      ),
    );
    const selection = el("select");
    selection.id = "inventory-contest";
    contestLabel.append(selection);
    const detail = el("section");
    detail.id = "inventory-detail";
    detail.tabIndex = -1;
    anchor.append(authorityLabel, contestLabel, detail);
    const available = () =>
      value.contests.filter(
        (c) =>
          authority.value === "all" ||
          c.occurrences.some((o) => o.source_id === authority.value),
      );
    function drawChoices() {
      onActions(null);
      onRead();
      const placeholder = el(
        "option",
        text("Choose a contest", "Elija un concurso"),
      );
      placeholder.value = "";
      selection.replaceChildren(placeholder);
      detail.replaceChildren();
      for (const [kind, label] of [
        [
          "candidate_election",
          text("Candidate elections", "Elecciones de candidatos"),
        ],
        [
          "judicial_retention",
          text("Judicial retention", "Retención judicial"),
        ],
        ["measure", text("Measures", "Medidas")],
      ]) {
        const group = el("optgroup");
        group.label = label;
        for (const c of available().filter((c) => c.kind === kind)) {
          const o = el("option", c.label);
          o.value = c.id;
          group.append(o);
        }
        if (group.children.length) selection.append(group);
      }
    }
    function drawContest() {
      onActions(null);
      onRead();
      const contest = available().find((c) => c.id === selection.value);
      detail.replaceChildren();
      if (!contest) return;
      detail.append(
        el("h3", contest.label),
        el(
          "p",
          text(
            "Public notice context only. No residential or personal ballot assignment is inferred.",
            "Solo contexto del aviso público. No se infiere residencia ni asignación a una boleta personal.",
          ),
        ),
      );
      if (language === "es") detail.append(el("p", translationNote));
      let readingButton = null;
      for (const occurrence of contest.occurrences.filter(
        (o) => authority.value === "all" || o.source_id === authority.value,
      )) {
        const source = value.sources[occurrence.source_id],
          section = el("section");
        section.append(
          el("h4", source.publisher),
          el("p", source.jurisdiction),
        );
        if (contest.kind === "candidate_election") {
          section.append(
            el(
              "p",
              text(
                "Printed order, not a ranking. Names and party codes preserve this source's spelling.",
                "Orden impreso, no una clasificación. Los nombres y códigos de partido conservan la escritura de esta fuente.",
              ),
            ),
          );
          section.append(
            el(
              "p",
              text("Printed instruction: ", "Instrucción impresa: ") +
                occurrence.instruction.text +
                " · " +
                text("page ", "página ") +
                occurrence.instruction.page,
            ),
          );
          const list = el("ul");
          for (const row of occurrence.candidate_rows) {
            const li = el("li");
            li.append(
              el("h4", row.printed_name),
              el(
                "p",
                text("Printed party code: ", "Código de partido impreso: ") +
                  row.printed_party,
              ),
              el(
                "p",
                text(
                  "Official background evidence not yet admitted. No position inferred from missing sources.",
                  "Información oficial de contexto aún no admitida. No se infieren posiciones por falta de fuentes.",
                ),
              ),
            );
            list.append(li);
          }
          section.append(list);
          for (const status of occurrence.source_statuses)
            section.append(
              el(
                "p",
                status.text +
                  " · " +
                  status.party +
                  text(
                    " · printed status, not a person",
                    " · estado impreso, no una persona",
                  ),
              ),
            );
          section.append(
            el(
              "p",
              text(
                "Write-in line printed. A complete eligible write-in register has not been verified.",
                "Aparece una línea para voto por escrito. No se ha verificado el registro completo de candidatos elegibles por escrito.",
              ),
            ),
          );
        } else {
          if (occurrence.wording) {
            const original = el("blockquote", occurrence.wording);
            original.lang = "en";
            original.className = "original-wording";
            section.append(
              el(
                "h4",
                text("Original English wording", "Texto original en inglés"),
              ),
              original,
            );
            if (contest.kind === "measure" && occurrence.source_id === "jceb")
              readingButton = mountReadingGuide(
                section,
                original,
                contest,
                occurrence,
                {
                  language,
                  readContext,
                  onRead,
                },
              );
          } else
            section.append(
              el(
                "p",
                text(
                  "Full wording remains in the linked original; a separate local transcription from this source has not been admitted.",
                  "El texto completo está en el original enlazado; no se ha admitido una transcripción local de esta fuente.",
                ),
              ),
            );
          section.append(
            el(
              "p",
              text("Printed choices: YES / NO", "Opciones impresas: YES / NO"),
            ),
          );
          if (contest.kind === "judicial_retention")
            section.append(
              el(
                "p",
                text(
                  "Judge background and performance evidence not admitted. No retention recommendation.",
                  "No se han admitido fuentes de contexto o desempeño del juez. No se recomienda cómo votar.",
                ),
              ),
            );
          else
            section.append(
              el(
                "p",
                text(
                  "Fresh explanation and Yes/No interpretation are not yet admitted for this item. Read the complete official wording; its claims are not independent findings.",
                  "No se ha admitido una explicación nueva ni una interpretación de Sí y No para este elemento. Consulte el texto oficial completo; sus afirmaciones no son conclusiones independientes.",
                ),
              ),
            );
        }
        section.append(
          link(
            source.url +
              (source.url.includes("drive.google.com")
                ? ""
                : "#page=" + occurrence.page),
            source.publisher +
              " · " +
              text("page ", "página ") +
              occurrence.page +
              " · " +
              text("original", "original"),
          ),
        );
        const sourceDetails = el("details");
        sourceDetails.append(
          el("summary", text("Source details", "Detalles de la fuente")),
          el(
            "p",
            text("Document date: ", "Fecha del documento: ") +
              source.document_date +
              " · " +
              text("Retrieved: ", "Obtenido: ") +
              source.retrieved_utc,
          ),
          el(
            "p",
            text(
              "Document version · SHA256 ",
              "Versión del documento · SHA256 ",
            ) + source.original_sha256,
          ),
        );
        sourceDetails.ontoggle = () => {
          if (sourceDetails.open) onRead();
        };
        section.append(sourceDetails);
        section.append(
          el(
            "p",
            occurrence.source_id === "kceb"
              ? text(
                  "Retained October 9 snapshot. Current authority link rechecked October 24; current PDF bytes not re-fetched. Subject to change.",
                  "Copia guardada el 9 de octubre. Enlace de la autoridad comprobado el 24 de octubre; no se volvió a descargar el PDF. Puede cambiar.",
                )
              : text(
                  "Re-fetched October 24; matches the retained version. Human acceptance remains pending.",
                  "Descargado de nuevo el 24 de octubre; coincide con la versión guardada. Aceptación humana pendiente.",
                ),
          ),
        );
        detail.append(section);
      }
      const sourceCheckButton = mountSourceCheck(detail, { language, onRead });
      const recap = el("section");
      recap.tabIndex = -1;
      const recapButton = button(
        detail,
        text("Recap this source", "Resumir esta fuente"),
        () => {
          onRead();
          recap.replaceChildren(
            el(
              "h4",
              text(
                "Source recap · this tab only",
                "Resumen de la fuente · solo en esta pestaña",
              ),
            ),
          );
          recap.append(
            el("p", contest.label),
            el(
              "p",
              text(
                "This is a public-notice selection, not a verified personal ballot. Background explanations, individual applicability and eligible write-ins remain unresolved. No vote choice is saved.",
                "Esta es una selección de un aviso público, no una boleta personal verificada. Siguen sin resolverse las fuentes de contexto, la aplicabilidad personal y los candidatos elegibles por escrito. No se guarda una elección de voto.",
              ),
            ),
          );
          const marked = detail.querySelector("mark");
          if (marked) {
            const quote = el("blockquote", marked.textContent);
            quote.lang = "en";
            recap.append(
              el(
                "p",
                text(
                  "Selected original passage · JCEB",
                  "Pasaje original seleccionado · JCEB",
                ),
              ),
              quote,
            );
          }
          for (const occurrence of contest.occurrences.filter(
            (o) => authority.value === "all" || o.source_id === authority.value,
          )) {
            const source = value.sources[occurrence.source_id];
            recap.append(
              link(
                source.url +
                  (occurrence.source_id === "jceb"
                    ? "#page=" + occurrence.page
                    : ""),
                source.publisher +
                  " · " +
                  text("page ", "página ") +
                  occurrence.page,
              ),
            );
          }
          recap.focus();
        },
      );
      const challengeButton = button(
        detail,
        text(
          "This transcription may be wrong",
          "Esta transcripción puede estar equivocada",
        ),
        () => {
          onActions(null);
          onRead();
          const originals = contest.occurrences.filter(
            (o) => authority.value === "all" || o.source_id === authority.value,
          );
          detail.replaceChildren(
            el("h3", contest.label),
            el(
              "p",
              text(
                "The transcription has been withdrawn from this view. Compare the original below. No report was sent and the source registry was not changed; a staffed correction service is not connected.",
                "Se retiró la transcripción de esta vista. Consulte el original a continuación. No se envió ningún informe ni se cambió el registro de fuentes; no hay un servicio de correcciones conectado.",
              ),
            ),
          );
          for (const occurrence of originals) {
            const source = value.sources[occurrence.source_id];
            detail.append(
              link(
                source.url +
                  (occurrence.source_id === "jceb"
                    ? "#page=" + occurrence.page
                    : ""),
                source.publisher +
                  " · " +
                  text("page ", "página ") +
                  occurrence.page,
              ),
            );
          }
          button(
            detail,
            text(
              "Show saved transcription again",
              "Mostrar de nuevo la transcripción guardada",
            ),
            drawContest,
          );
          detail.focus();
        },
      );
      detail.append(recap);
      let officeButton = null;
      const family = officeFamily(contest);
      if (family) {
        const officeHost = el("section");
        officeButton = button(
          detail,
          text("What does this office do?", "¿Qué hace este cargo?"),
          () => void onOffice(officeHost, family),
        );
        detail.append(officeHost);
      }
      if (contest.kind === "candidate_election" && !family)
        detail.append(
          el(
            "p",
            text(
              "Verified office responsibilities and term information have not been loaded for this contest.",
              "No se han cargado aquí fuentes verificadas sobre las funciones y el mandato de este cargo.",
            ),
          ),
        );
      if (contest.id === "proposition-a")
        button(
          detail,
          text(
            "Explore Proposition A with official maps",
            "Explorar la Proposición A con mapas oficiales",
          ),
          () => void onMeasure(),
        );
      const invoke = (control) => () => {
        if (control.isConnected && !control.disabled) {
          control.focus();
          control.click();
        }
      };
      onActions({
        id: authority.value + ":" + contest.id,
        title: contest.label,
        source_version: INVENTORY_VERSION,
        actions: {
          source: () => detail.querySelector("a.source-link")?.focus(),
          source_check: invoke(sourceCheckButton),
          recap: invoke(recapButton),
          challenge: invoke(challengeButton),
          ...(readingButton ? { read_parts: invoke(readingButton) } : {}),
          ...(officeButton ? { office: invoke(officeButton) } : {}),
        },
      });
    }
    authority.onchange = drawChoices;
    selection.onchange = drawContest;
    drawChoices();
  } catch {
    if (anchor.isConnected)
      anchor.textContent = text(
        "The official inventory could not be checked. No partial roster or invented candidates are shown. Choose the topic again deliberately.",
        "No se pudo comprobar el inventario oficial. No se muestra una lista parcial ni se inventan candidatos. Elija el tema de nuevo si desea intentarlo.",
      );
  }
}
