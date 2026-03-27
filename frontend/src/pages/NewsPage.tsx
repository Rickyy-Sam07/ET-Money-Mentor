import { useEffect, useState } from "react";
import { getNews } from "../lib/api";
import { loadNewsItems, saveNewsItems } from "../lib/voiceState";

export function NewsPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    async function load() {
      const cached = loadNewsItems<any[]>();
      if (cached && cached.length > 0) {
        setItems(cached);
      }
      const data = await getNews();
      const latest = data.items || [];
      setItems(latest);
      saveNewsItems(latest);
    }
    void load();
  }, []);

  return (
    <section className="card">
      <h2>News & Warnings</h2>
      <div className="news-list">
        {items.map((item, idx) => (
          <article key={idx} className={item.warning ? "news-item news-warning" : "news-item"}>
            <h3>{item.title}</h3>
            <p>{item.summary}</p>
            <p><strong>Impact:</strong> {item.impact}</p>
            <p className="muted">Source: {item.source} | Sentiment: {item.sentiment}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
