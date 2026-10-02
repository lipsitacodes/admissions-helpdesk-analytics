import React from "react";
import {
  GraduationCap,
  MapPin,
  IndianRupee,
  Building2,
  ExternalLink,
  Globe,
  Info,
  CheckCircle2,
  FileText,
  Phone,
  Mail,
} from "lucide-react";

/**
 * Parses inline markdown (e.g. **bold**, [label](url), urls, phone numbers, emails) into React elements.
 */
function renderInlineMarkdown(text) {
  if (!text) return "";
  const parts = [];
  const regex = /(\*\*([^*]+)\*\*|\[([^\]]+)\]\((https?:\/\/[^\s\)]+)\)|(https?:\/\/[^\s\)]+)|(\b8260077222\b|\+?91[- ]?[6-9]\d{9})|([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+))/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    if (match[2]) {
      // **bold**
      parts.push(
        <strong key={`b-${match.index}`} className="font-bold text-light-text dark:text-dark-text">
          {match[2]}
        </strong>
      );
    } else if (match[3] && match[4]) {
      // [label](url)
      parts.push(
        <a
          key={`l-${match.index}`}
          href={match[4]}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 underline decoration-blue-500/40 hover:decoration-blue-500 transition-colors"
        >
          <span>{match[3]}</span>
          <ExternalLink className="w-3 h-3 opacity-80" />
        </a>
      );
    } else if (match[5]) {
      // Raw URL
      let url = match[5];
      let trailing = "";
      const puncMatch = url.match(/[.,!?;:]+$/);
      if (puncMatch) {
        trailing = puncMatch[0];
        url = url.slice(0, -trailing.length);
      }
      const displayLabel = url.replace(/^https?:\/\/(www\.)?/, "");
      parts.push(
        <a
          key={`u-${match.index}`}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 underline decoration-blue-500/40 hover:decoration-blue-500 transition-colors"
        >
          <span>{displayLabel}</span>
          <ExternalLink className="w-3 h-3 opacity-80" />
        </a>
      );
      if (trailing) {
        parts.push(trailing);
      }
    } else if (match[6]) {
      // Phone number
      const phoneDigits = match[6].replace(/\D/g, "");
      parts.push(
        <a
          key={`p-${match.index}`}
          href={`tel:${phoneDigits}`}
          className="inline-flex items-center gap-1.5 font-bold text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 underline decoration-emerald-500/40 hover:decoration-emerald-500 transition-colors"
          title={`Call ${match[6]}`}
        >
          <Phone className="w-3 h-3 opacity-80" />
          <span>{match[6]}</span>
        </a>
      );
    } else if (match[7]) {
      // Email address
      const email = match[7];
      parts.push(
        <a
          key={`m-${match.index}`}
          href={`mailto:${email}`}
          className="inline-flex items-center gap-1.5 font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 underline decoration-indigo-500/40 hover:decoration-indigo-500 transition-colors"
          title={`Email ${email}`}
        >
          <Mail className="w-3 h-3 opacity-80" />
          <span>{email}</span>
        </a>
      );
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}

/**
 * Maps field names to distinct icons and theme colors.
 */
function getFieldIcon(key) {
  const lower = key.toLowerCase();
  if (
    lower.includes("phone") ||
    lower.includes("helpline") ||
    lower.includes("contact") ||
    lower.includes("call") ||
    key.includes("नंबर") ||
    key.includes("ନମ୍ବର")
  ) {
    return <Phone className="w-4 h-4 text-emerald-500 shrink-0" />;
  }
  if (
    lower.includes("website") ||
    lower.includes("portal") ||
    lower.includes("site") ||
    key.includes("वेबसाइट") ||
    key.includes("ୱେବସାଇଟ୍")
  ) {
    return <Globe className="w-4 h-4 text-sky-500 shrink-0" />;
  }
  if (
    lower.includes("email") ||
    lower.includes("mail") ||
    key.includes("ईमेल") ||
    key.includes("ଇମେଲ୍")
  ) {
    return <Mail className="w-4 h-4 text-indigo-500 shrink-0" />;
  }
  if (lower.includes("course") || lower.includes("program") || key.includes("कोर्स") || key.includes("କୋର୍ସ")) {
    return <GraduationCap className="w-4 h-4 text-violet-500 shrink-0" />;
  }
  if (lower.includes("campus") || lower.includes("location") || key.includes("कैंपस") || key.includes("କ୍ୟାମ୍ପସ")) {
    return <MapPin className="w-4 h-4 text-rose-500 shrink-0" />;
  }
  if (lower.includes("fee") || lower.includes("cost") || lower.includes("tuition") || key.includes("फीस") || key.includes("ଫିସ୍") || key.includes("शुल्क") || key.includes("ଟଙ୍କା")) {
    return <IndianRupee className="w-4 h-4 text-emerald-500 shrink-0" />;
  }
  if (lower.includes("faculty") || lower.includes("department") || lower.includes("school") || key.includes("फैकल्टी") || key.includes("ଫ୍ୟାକଲ୍ଟି") || key.includes("विभाग") || key.includes("ବିଭାଗ")) {
    return <Building2 className="w-4 h-4 text-amber-500 shrink-0" />;
  }
  return <CheckCircle2 className="w-4 h-4 text-sky-500 shrink-0" />;
}

export function FormattedAnswer({ text }) {
  if (!text) return null;

  const rawLines = text.split(/\r?\n/);
  const elements = [];
  let currentKeyValues = [];
  let introLines = [];
  let noticeLines = [];
  let sourceLink = null;

  const flushKeyValues = () => {
    if (currentKeyValues.length > 0) {
      const items = [...currentKeyValues];
      elements.push(
        <div
          key={`kv-group-${elements.length}`}
          className="my-3 rounded-xl border border-light-border dark:border-dark-border bg-light-surface/60 dark:bg-dark-surface/60 p-3 sm:p-4 space-y-2.5 shadow-xs"
        >
          {items.map((item, idx) => {
            const isFee =
              item.key.toLowerCase().includes("fee") ||
              item.key.includes("फीस") ||
              item.key.includes("ଫିସ୍") ||
              item.key.includes("शुल्क") ||
              item.key.includes("ଟଙ୍କା");
            return (
              <div
                key={idx}
                className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 sm:gap-4 py-1.5 border-b border-light-border/40 dark:border-dark-border/40 last:border-b-0"
              >
                <div className="flex items-center gap-2 text-xs font-semibold text-light-muted dark:text-dark-muted shrink-0">
                  {getFieldIcon(item.key)}
                  <span>{item.key}:</span>
                </div>
                <div className="text-xs sm:text-sm text-left sm:text-right font-medium text-light-text dark:text-dark-text break-words">
                  {isFee ? (
                    <span className="inline-block px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/25 text-emerald-600 dark:text-emerald-400 font-bold">
                      {renderInlineMarkdown(item.value)}
                    </span>
                  ) : (
                    renderInlineMarkdown(item.value)
                  )}
                </div>
              </div>
            );
          })}
        </div>
      );
      currentKeyValues = [];
    }
  };

  const flushIntro = () => {
    if (introLines.length > 0) {
      elements.push(
        <div
          key={`intro-${elements.length}`}
          className="text-xs sm:text-sm font-medium text-light-text dark:text-dark-text leading-relaxed space-y-1.5"
        >
          {introLines.map((line, lIdx) => {
            if (line.startsWith("###")) {
              const cleanH = line.replace(/^#{1,4}\s*/, "");
              return (
                <h4
                  key={lIdx}
                  className="font-bold text-xs sm:text-sm text-blue-600 dark:text-blue-400 pt-2 pb-0.5 tracking-tight"
                >
                  {renderInlineMarkdown(cleanH)}
                </h4>
              );
            }
            if (/^[•\-\*]\s+/.test(line)) {
              const cleanBullet = line.replace(/^[•\-\*]\s+/, "");
              return (
                <div key={lIdx} className="flex items-start gap-2.5 pl-1 py-0.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500/80 dark:bg-blue-400/80 shrink-0 mt-1.5" />
                  <span className="flex-1">{renderInlineMarkdown(cleanBullet)}</span>
                </div>
              );
            }
            return <p key={lIdx}>{renderInlineMarkdown(line)}</p>;
          })}
        </div>
      );
      introLines = [];
    }
  };

  for (let i = 0; i < rawLines.length; i++) {
    const line = rawLines[i].trim();
    if (!line) continue;

    // Detect Source Link: matches "- 🔗 **Official Source:** [label](url)" or "🔗 Official Source: https://..." or with any phrasing
    const sourceMatch =
      line.match(
        /(?:🔗|🌐)?\s*\*?\*?(?:Official Source|आधिकारिक स्रोत|ଅଫିସିଆଲ୍ ସୂତ୍ର|Source|स्रोत|ସୂତ୍ର)[^*:]*\*?\*?:\s*(?:\[([^\]]*)\]\((https?:\/\/[^\s\)]+)\)|\[?(https?:\/\/[^\s\]\)]+)\]?)/i
      ) ||
      line.match(/\[([^\]]*(?:view\s*more|source|स्रोत|ସୂତ୍ର)[^\]]*)\]\((https?:\/\/[^\s\)]+)\)/i);

    if (sourceMatch) {
      flushIntro();
      flushKeyValues();
      sourceLink = sourceMatch[2] || sourceMatch[3] || sourceMatch[1];
      continue;
    }

    // Detect Notice Callout
    if (line.startsWith(">") || line.includes("ℹ️") || line.toLowerCase().includes("notice:")) {
      flushIntro();
      flushKeyValues();
      const cleanNotice = line
        .replace(/^>\s*/, "")
        .replace(/ℹ️\s*/, "")
        .replace(/\*\*Notice:\*\*\s*/i, "")
        .replace(/\*\*Notice on Requested Information\*\*:\s*/i, "");
      if (cleanNotice.trim()) {
        noticeLines.push(cleanNotice.trim());
      }
      continue;
    }

    // Detect Key-Value List Lines: "- **Key:** Value" or "• **Key**: Value" or "**Key:** Value"
    // Must be a bullet line OR have a compact title-like key (<= 35 chars without periods/slashes)
    const isBullet = /^[•\-\*]\s+/.test(line);
    const kvMatch = line.match(/^(?:[•\-\*]\s+)?\*?\*?([^:*]+?)\*?\*?:\s*(.+)$/);
    if (
      kvMatch &&
      !line.toLowerCase().startsWith("http") &&
      (isBullet || (kvMatch[1].trim().length <= 35 && !kvMatch[1].includes(".") && !kvMatch[1].includes("/")))
    ) {
      flushIntro();
      const rawKey = kvMatch[1].replace(/\*\*/g, "").trim();
      const rawVal = kvMatch[2].replace(/\*\*/g, "").trim();
      currentKeyValues.push({ key: rawKey, value: rawVal });
      continue;
    }

    // General text / intro lines
    if (currentKeyValues.length > 0) {
      flushKeyValues();
    }
    introLines.push(line);
  }

  flushIntro();
  flushKeyValues();

  const isHindi = /[\u0900-\u097F]/.test(text);
  const isOdia = /[\u0B00-\u0B7F]/.test(text);
  const noticeHeader = isOdia ? "ଆଡମିଶନ ସୂଚନା" : isHindi ? "एडमिशन सूचना" : "Admissions Notice";
  const verifiedBadge = isOdia ? "ଯାଞ୍ଚ ହୋଇଥିବା ଲିଙ୍କ" : isHindi ? "सत्यापित लिंक" : "verified official link";

  // Render Notices
  if (noticeLines.length > 0) {
    elements.push(
      <div
        key={`notices-${elements.length}`}
        className="my-3 p-3 rounded-xl border border-sky-500/20 bg-sky-500/10 text-sky-900 dark:text-sky-200 text-xs flex items-start gap-2.5"
      >
        <Info className="w-4 h-4 text-sky-500 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-bold text-[11px] uppercase tracking-wider text-sky-600 dark:text-sky-400">
            {noticeHeader}
          </p>
          {noticeLines.map((n, idx) => (
            <p key={idx} className="leading-relaxed opacity-90">
              {renderInlineMarkdown(n)}
            </p>
          ))}
        </div>
      </div>
    );
  }

  // Render Interactive "View More" Button
  if (sourceLink) {
    elements.push(
      <div
        key="official-source-link"
        className="mt-3.5 pt-3 border-t border-light-border/40 dark:border-dark-border/40 flex items-center justify-between gap-3 flex-wrap"
      >
        <a
          href={sourceLink}
          target="_blank"
          rel="noopener noreferrer"
          id="view-more-source-btn"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 shadow-md hover:shadow-indigo-500/25 active:scale-95 transition-all cursor-pointer no-underline group"
          title="Open official university course page"
        >
          <Globe className="w-3.5 h-3.5 text-blue-200 group-hover:rotate-12 transition-transform" />
          <span className="tracking-wide">View More</span>
          <ExternalLink className="w-3.5 h-3.5 text-blue-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
        </a>
        <span className="text-[11px] text-light-muted dark:text-dark-muted font-mono inline-flex items-center gap-1.5 bg-light-surface/80 dark:bg-dark-surface/80 px-2.5 py-1 rounded-lg border border-light-border/30 dark:border-dark-border/30">
          <CheckCircle2 className="w-3 h-3 text-emerald-500" />
          <span>{verifiedBadge}</span>
        </span>
      </div>
    );
  }

  // Fallback if parsing produced nothing
  if (elements.length === 0) {
    return <div className="whitespace-pre-wrap leading-relaxed">{renderInlineMarkdown(text)}</div>;
  }

  return <div className="space-y-2">{elements}</div>;
}

export default FormattedAnswer;
