import { loadBrowseInventory, officeFamily } from "./office-source.mjs";
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
const originalUrl = (source, occurrence) =>
  source.url +
  (source.url.includes("drive.google.com") ? "" : "#page=" + occurrence.page);
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
    onRecap,
    onWithdraw,
    translationNote,
    initialSelection = null,
    onSelection = () => {},
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
    const value = await loadBrowseInventory(
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
      el(
        "h3",
        text(
          "Kansas City, then Jackson County",
          "Kansas City, después Jackson County",
        ),
      ),
    );
    const context = el("p");
    context.id = "inventory-context";
    context.setAttribute("role", "status");
    anchor.append(
      context,
      el(
        "p",
        text(
          "Start with the actual W1-P7 public sample. The county comparison uses a broader JCEB notice: a second individual ballot style has not been verified. No personal ballot or final write-in eligibility is established.",
          "Empiece por la muestra pública W1-P7. La comparación del condado usa un aviso más amplio de JCEB: no se ha verificado un segundo estilo individual de boleta. No se establece una boleta personal ni la elegibilidad final de candidatos por escrito.",
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
      [
        "kc-sample",
        text("Kansas City · W1-P7 sample", "Kansas City · muestra W1-P7"),
      ],
      [
        "jceb",
        text(
          "JCEB · notice outside Kansas City",
          "JCEB · aviso fuera de Kansas City",
        ),
      ],
      ["kceb", text("KCEB · broader notice", "KCEB · aviso más amplio")],
      ["all", text("Both notices · union", "Ambos avisos · conjunto")],
    ]) {
      const option = el("option", label);
      option.value = id;
      authority.append(option);
    }
    authorityLabel.append(authority);
    const contestLabel = el(
      "label",
      text(
        "Choose a printed contest · application label",
        "Elija un concurso impreso · etiqueta de la aplicación",
      ),
    );
    const selection = el("select");
    selection.id = "inventory-contest";
    contestLabel.append(selection);
    const detail = el("section");
    detail.id = "inventory-detail";
    detail.tabIndex = -1;
    const examples = el("div");
    examples.className = "question-examples";
    button(
      examples,
      text(
        "KC example · candidates for U.S. House",
        "Ejemplo de KC · candidatos a la Cámara federal",
      ),
      () => selectExample("kc-sample", "us-house-5"),
    );
    button(
      examples,
      text(
        "County comparison · Independence bond",
        "Comparación del condado · bono de Independence",
      ),
      () => selectExample("jceb", "independence-bond-1"),
    );
    anchor.append(examples, authorityLabel, contestLabel, detail);
    const inContext = (o) =>
      authority.value === "all"
        ? o.source_id !== "kc-sample"
        : o.source_id === authority.value;
    const available = () =>
      value.contests.filter((c) => c.occurrences.some(inContext));
    function selectExample(source, contest) {
      authority.value = source;
      drawChoices();
      selection.value = contest;
      drawContest();
      detail.focus();
    }
    function drawChoices() {
      onActions(null);
      onRead();
      onSelection({ source: authority.value, contest: "" });
      const choices = available();
      context.textContent =
        (authority.value === "kc-sample"
          ? text(
              "W1-P7 · 2-page public sample",
              "W1-P7 · muestra pública de 2 páginas",
            )
          : text(
              "Public notice context · not one ballot style",
              "Contexto de aviso público · no es un estilo individual de boleta",
            )) +
        " · " +
        choices.length +
        text(" printed contests", " concursos impresos") +
        " · " +
        choices.filter((c) => c.kind === "candidate_election").length +
        text(" candidate elections", " elecciones de candidatos") +
        " · " +
        choices.filter((c) => c.kind === "judicial_retention").length +
        text(" judicial retentions", " retenciones judiciales") +
        " · " +
        choices.filter((c) => c.kind === "measure").length +
        text(" measures", " medidas");
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
      onSelection({ source: authority.value, contest: contest?.id ?? "" });
      detail.replaceChildren();
      if (!contest) return;
      detail.append(
        el("h3", contest.label),
        el(
          "p",
          text(
            "Selected public-source context only. No residential or personal ballot assignment is inferred.",
            "Solo contexto de la fuente pública seleccionada. No se infiere residencia ni asignación a una boleta personal.",
          ),
        ),
      );
      if (language === "es") detail.append(el("p", translationNote));
      let readingButton = null;
      if (authority.value === "jceb" && contest.id === "independence-bond-1")
        detail.append(
          el(
            "p",
            text(
              "This municipal question appears in the JCEB notice and is absent from the W1-P7 sample. Its presence in the notice does not place it on every JCEB resident's ballot. No candidate contest is assigned alongside it.",
              "Esta pregunta municipal aparece en el aviso de JCEB y no aparece en la muestra W1-P7. Su presencia en el aviso no significa que esté en la boleta de cada residente de JCEB. No se le asigna un concurso de candidatos junto a ella.",
            ),
          ),
        );
      for (const occurrence of contest.occurrences.filter(inContext)) {
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
              el("strong", row.printed_name),
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
          else if (contest.id !== "proposition-a")
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
            originalUrl(source, occurrence),
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
        if (source.freshness) {
          const freshness = el("p", source.freshness);
          freshness.lang = "en";
          sourceDetails.append(freshness);
        }
        section.append(sourceDetails);
        section.append(
          el(
            "p",
            text(
              "Retained public source · retrieved ",
              "Fuente pública guardada · obtenida ",
            ) +
              source.retrieved_utc.slice(0, 10) +
              text(
                ". Current certification and human acceptance remain unverified. See version details for refresh limits.",
                ". Certificación actual y aceptación humana sin verificar. Consulte los límites de actualización en los detalles de la versión.",
              ),
          ),
        );
        detail.append(section);
      }
      const sourceCheckButton = mountSourceCheck(detail, { language, onRead });
      const recapButton = button(
        detail,
        text("Add this source to my recap", "Agregar esta fuente a mi resumen"),
        () => {
          onRead();
          onRecap(
            contest.occurrences.filter(inContext).map((o) => ({
              source_id: o.source_id,
              contest_id: contest.id,
              browse_version: value.browse_version,
            })),
            value,
          );
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
          const originals = contest.occurrences.filter(inContext);
          const explanationsWithdrawn = onWithdraw(
            contest.id,
            originals.map((o) => o.source_id),
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
          if (contest.id === "proposition-a")
            detail.append(
              el(
                "p",
                explanationsWithdrawn
                  ? text(
                      "This also withdraws any related W1-P7 AI explanations from this session and recap.",
                      "Esto también retira de esta sesión y del resumen cualquier explicación por IA de W1-P7 relacionada.",
                    )
                  : text(
                      "This does not withdraw W1-P7 explanations, which cite a different retained source context.",
                      "Esto no retira las explicaciones de W1-P7, que citan otro contexto de fuente guardada.",
                    ),
              ),
            );
          for (const occurrence of originals) {
            const source = value.sources[occurrence.source_id];
            detail.append(
              link(
                originalUrl(source, occurrence),
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
      if (contest.id === "proposition-a") {
        detail.append(
          el(
            "p",
            text(
              "Explore the Proposition A question and the application's Yes/No meanings with official maps. Complete printed wording is in the linked original; the W1-P7 context also transcribes its fiscal estimate.",
              "Explore la pregunta de la Proposición A y las explicaciones de Sí y No de la aplicación con mapas oficiales. El texto impreso completo está en el original enlazado; el contexto W1-P7 también transcribe su estimación fiscal.",
            ),
          ),
        );
        button(
          detail,
          text(
            "Explore Proposition A with official maps",
            "Explorar la Proposición A con mapas oficiales",
          ),
          () => void onMeasure(),
        );
      }
      const invoke = (control) => () => {
        if (control.isConnected && !control.disabled) {
          control.focus();
          control.click();
        }
      };
      onActions({
        id: authority.value + ":" + contest.id,
        title: contest.label,
        source_version: value.browse_version,
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
    if (
      initialSelection &&
      [...authority.options].some((o) => o.value === initialSelection.source)
    )
      authority.value = initialSelection.source;
    drawChoices();
    if (
      initialSelection &&
      available().some((c) => c.id === initialSelection.contest)
    ) {
      selection.value = initialSelection.contest;
      drawContest();
    }
  } catch {
    if (anchor.isConnected)
      anchor.textContent = signal.aborted
        ? text(
            "Source loading stopped. Choose the topic again to reload.",
            "Se detuvo la carga. Elija el tema de nuevo para cargarlo.",
          )
        : text(
            "The official inventory could not be checked. No partial roster or invented candidates are shown. Choose the topic again deliberately.",
            "No se pudo comprobar el inventario oficial. No se muestra una lista parcial ni se inventan candidatos. Elija el tema de nuevo si desea intentarlo.",
          );
  }
}
