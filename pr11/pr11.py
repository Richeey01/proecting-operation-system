"""Практическая работа № 11: PCA, классификация и 2D-визуализация."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import sklearn
import umap
from sklearn.datasets import load_breast_cancer
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
PLOTS = ROOT / "plots"
PLOTS.mkdir(exist_ok=True)
plt.rcParams["font.family"] = "DejaVu Sans"


def scatter(ax, points, labels, title, names, xlabel="Компонента 1", ylabel="Компонента 2"):
    for class_id, color in [(0, "#c44758"), (1, "#287ca7")]:
        selected = labels == class_id
        ax.scatter(
            points[selected, 0], points[selected, 1],
            s=20, alpha=0.72, c=color, label=names[class_id],
            edgecolors="none", rasterized=True,
        )
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)


def make_pipeline(variance=None):
    steps = [("scaler", StandardScaler())]
    if variance is not None:
        steps.append(("pca", PCA(n_components=variance, svd_solver="full")))
    steps.append(("model", LogisticRegression(max_iter=3000, random_state=42)))
    return Pipeline(steps)


def neighbor_overlap(a, b, k=15):
    """Средняя доля общих соседей каждой точки в двух 2D-проекциях."""
    ia = NearestNeighbors(n_neighbors=k + 1).fit(a).kneighbors(return_distance=False)[:, :k]
    ib = NearestNeighbors(n_neighbors=k + 1).fit(b).kneighbors(return_distance=False)[:, :k]
    return float(np.mean([len(set(x) & set(y)) / k for x, y in zip(ia, ib)]))


def main():
    data = load_breast_cancer()
    x, y = data.data, data.target
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"Данные: {x.shape}; train: {x_train.shape}; test: {x_test.shape}")

    # Уровень A. Обучаем scaler и PCA только на обучающей выборке.
    scaler = StandardScaler()
    train_scaled = scaler.fit_transform(x_train)
    test_scaled = scaler.transform(x_test)
    pca = PCA(svd_solver="full").fit(train_scaled)
    ratios = pca.explained_variance_ratio_
    cumulative = np.cumsum(ratios)
    k90 = int(np.searchsorted(cumulative, 0.90) + 1)
    pca_2d = pca.transform(train_scaled)[:, :2]
    print("\nУровень A")
    print("explained_variance_ratio_:", np.array2string(ratios, precision=5))
    print(f"90% дисперсии: {k90} компонент; первые две: {cumulative[1]:.4%}")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(np.arange(1, len(cumulative) + 1), cumulative * 100, marker="o", ms=3)
    ax.axhline(90, ls="--", c="#c44758", label="Порог 90%")
    ax.axvline(k90, ls="--", c="#25805a", label=f"{k90} компонент")
    ax.set(xlabel="Число компонент", ylabel="Накопленная объяснённая дисперсия, %",
           title="PCA: накопленная объяснённая дисперсия", ylim=(0, 103))
    ax.set_xticks(np.arange(1, len(cumulative) + 1, 2))
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS / "01_cumulative_variance.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter(ax, pca_2d, y_train, "PCA: обучающая выборка", data.target_names,
            f"PC1 ({ratios[0]:.1%})", f"PC2 ({ratios[1]:.1%})")
    fig.tight_layout()
    fig.savefig(PLOTS / "02_pca_2d.png", dpi=160)
    plt.close(fig)

    # Уровень B. Каждый этап pipeline обучается внутри своего CV-разбиения.
    print("\nУровень B")
    variants = {"Без PCA": None, "PCA 80%": 0.80, "PCA 90%": 0.90, "PCA 95%": 0.95}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    fitted = {}
    for name, variance in variants.items():
        model = make_pipeline(variance)
        scores = cross_validate(model, x_train, y_train, cv=cv, scoring="accuracy", n_jobs=1)
        model.fit(x_train, y_train)
        features = x_train.shape[1] if variance is None else int(model.named_steps["pca"].n_components_)
        results[name] = {
            "cv_accuracy_mean": float(scores["test_score"].mean()),
            "cv_accuracy_std": float(scores["test_score"].std()),
            "cv_fit_time_mean_s": float(scores["fit_time"].mean()),
            "cv_fit_time_std_s": float(scores["fit_time"].std()),
            "features_to_classifier": features,
        }
        fitted[name] = model
        print(f"{name:8s} | CV accuracy {results[name]['cv_accuracy_mean']:.4f} "
              f"| fit {results[name]['cv_fit_time_mean_s']:.4f} с | {features} признаков")
    best = max((name for name in variants if name != "Без PCA"),
               key=lambda name: results[name]["cv_accuracy_mean"])
    for name in ("Без PCA", best):
        results[name]["test_accuracy"] = float(accuracy_score(y_test, fitted[name].predict(x_test)))
        print(f"Тест {name}: accuracy {results[name]['test_accuracy']:.4f}")
    print(f"Лучший вариант PCA по CV: {best}")

    # Уровень C. Все методы получают одни и те же train-объекты после масштабирования.
    print("\nУровень C")
    tsne_models, tsne_views = {}, {}
    for perplexity in (5, 30, 50):
        print(f"t-SNE perplexity={perplexity}...")
        model = TSNE(n_components=2, perplexity=perplexity, init="pca",
                     learning_rate="auto", max_iter=1000, random_state=42)
        tsne_views[perplexity] = model.fit_transform(train_scaled)
        tsne_models[perplexity] = model
    print("UMAP...")
    umap_model = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1,
                           random_state=42, n_jobs=1)
    umap_2d = umap_model.fit_transform(train_scaled)

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    for ax, points, title in zip(axes, (pca_2d, tsne_views[30], umap_2d),
                                 ("PCA", "t-SNE (perplexity=30)", "UMAP")):
        scatter(ax, points, y_train, title, data.target_names)
    fig.tight_layout()
    fig.savefig(PLOTS / "03_methods_comparison.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    for ax, perplexity in zip(axes, (5, 30, 50)):
        scatter(ax, tsne_views[perplexity], y_train,
                f"t-SNE: perplexity={perplexity}", data.target_names)
    fig.tight_layout()
    fig.savefig(PLOTS / "04_tsne_perplexity.png", dpi=160)
    plt.close(fig)

    pca_new_shape = list(pca.transform(test_scaled[:5])[:, :2].shape)
    umap_new_shape = list(umap_model.transform(test_scaled[:5]).shape)
    try:
        tsne_models[30].transform(test_scaled[:5])
        tsne_has_transform = True
    except AttributeError:
        tsne_has_transform = False
    overlap_5_30 = neighbor_overlap(tsne_views[5], tsne_views[30])
    overlap_30_50 = neighbor_overlap(tsne_views[30], tsne_views[50])
    print(f"PCA transform: {pca_new_shape}; UMAP transform: {umap_new_shape}")
    print(f"t-SNE transform существует: {tsne_has_transform} (ожидается False)")
    print(f"Общие 15 соседей t-SNE: 5/30 {overlap_5_30:.1%}; 30/50 {overlap_30_50:.1%}")
    assert not tsne_has_transform
    assert pca_new_shape == umap_new_shape == [5, 2]

    summary = {
        "dataset": "Breast Cancer Wisconsin (sklearn)",
        "samples": len(x), "train_samples": len(x_train), "test_samples": len(x_test),
        "original_features": x.shape[1], "sklearn_version": sklearn.__version__,
        "umap_version": umap.__version__,
        "pca_90_components": k90, "pca_90_actual_variance": float(cumulative[k90 - 1]),
        "pca_first_two_variance": float(cumulative[1]),
        "models": results, "best_pca_by_cv": best,
        "tsne_has_transform": tsne_has_transform,
        "pca_new_shape": pca_new_shape, "umap_new_shape": umap_new_shape,
        "tsne_neighbor_overlap_5_30": overlap_5_30,
        "tsne_neighbor_overlap_30_50": overlap_30_50,
    }
    (ROOT / "results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Готово: 4 графика в plots/ и результаты в results.json")


if __name__ == "__main__":
    main()
