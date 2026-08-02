#!/usr/bin/env python3
"""mok-tua CLI — models · story · stack · process (discover/audit/pull/smoke/lock)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))


def _j(obj: object) -> None:
    print(json.dumps(obj, indent=2, default=str))


def _dry_flag(args: argparse.Namespace) -> bool:
    if getattr(args, "no_dry_run", False):
        return False
    if getattr(args, "live", False) or getattr(args, "live_still", False):
        return False
    return True


def main() -> int:
    p = argparse.ArgumentParser(
        prog="mok-tua",
        description=(
            "mok-tua v0.5 — director stack process\n"
            "  models: inventory|stage\n"
            "  story:  sides|run|batch\n"
            "  stack:  providers|doctor|launch|stop|pull|status\n"
            "  process: discover|audit|stage-app|smoke|lock\n"
            "  federation: packet|nodes|chains (ask_packet.v1 trusted lab)\n"
            "  ui: tui (--skin c64|modern)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # --- models ---
    inv = sub.add_parser("inventory", help="Model stage inventory on ai-data")
    inv.add_argument("-f", "--manifest", default=None)

    st = sub.add_parser("stage", help="Stage models into allowlisted pool subdirs")
    st.add_argument("-f", "--manifest", default=None)
    st.add_argument("--live", action="store_true")
    st.add_argument("--required-for", default="local_qwen_edit")
    st.add_argument("--only", nargs="*", default=None)

    # --- sides / run ---
    sides = sub.add_parser("sides", help="Ingest PDF/FDX/MD/TXT sides → story markdown")
    sides.add_argument("path")
    sides.add_argument("-o", "--out", default=None)
    sides.add_argument("--run", action="store_true")
    sides.add_argument("--live-still", action="store_true")
    sides.add_argument("--still-provider", default=None)
    sides.add_argument("--no-dry-run", action="store_true")

    runp = sub.add_parser("run", help="Create a run from story/sides file")
    runp.add_argument("path")
    runp.add_argument("--live-still", action="store_true")
    runp.add_argument("--still-provider", default=None)
    runp.add_argument("--video-provider", default=None)
    runp.add_argument("--qqq", default=None)
    runp.add_argument("--no-dry-run", action="store_true")

    bat = sub.add_parser("batch", help="Batch run multiple side/story files")
    bat.add_argument("paths", nargs="+")
    bat.add_argument("--live-still", action="store_true")
    bat.add_argument("--still-provider", default=None)
    bat.add_argument("--no-dry-run", action="store_true")

    # --- providers / launch ---
    prov = sub.add_parser("providers", help="List director stack providers")
    prov.add_argument("--tier", default=None)
    prov.add_argument("--role", default=None)
    prov.add_argument("--bleed", action="store_true")
    prov.add_argument("--json", action="store_true")
    prov.add_argument("--no-probe", action="store_true")

    doc = sub.add_parser("doctor", help="Full stack health board")
    doc.add_argument("--json", action="store_true")

    launch = sub.add_parser("launch", help="Launch a provider or named chain")
    launch.add_argument("target", help="provider id OR chain: demo|video|face|audio|body|full")
    launch.add_argument("--live", action="store_true", help="Actually spawn (default dry-run)")
    launch.add_argument("--force", action="store_true")
    launch.add_argument("--port", type=int, default=None)
    launch.add_argument("--json", action="store_true")

    stop = sub.add_parser("stop", help="Stop a mok-tua-spawned provider")
    stop.add_argument("provider_id")

    pull = sub.add_parser(
        "pull",
        help="git pull provider(s) — id | --tier T0_orchestrators | --all-bleed",
    )
    pull.add_argument("provider_id", nargs="?", default=None)
    pull.add_argument("--tier", default=None, help="e.g. T0_orchestrators, T1_vid_gen, …")
    pull.add_argument("--all-bleed", action="store_true", help="All bleeding_edge apps")
    pull.add_argument("--live", action="store_true")
    pull.add_argument("--force", action="store_true", help="Pull even if dirty (dangerous)")
    pull.add_argument(
        "--monitor",
        default=None,
        nargs="?",
        const="gpu-host",
        help="Sample host during live pull (default node: gpu-host)",
    )
    pull.add_argument("--priority-max", type=int, default=2)

    status = sub.add_parser("status", help="Alias for providers table + doctor grade")
    status.add_argument("--json", action="store_true")

    # --- process: discover / audit / smoke / lock ---
    disc = sub.add_parser("discover", help="Find Pinokio/GitHub options not in catalog")
    disc.add_argument(
        "--source",
        default="all",
        choices=["all", "pinokio", "github_mirrors", "catalog_gaps"],
    )
    disc.add_argument("--limit", type=int, default=40)
    disc.add_argument("--json", action="store_true")

    aud = sub.add_parser("audit", help="Audit id/path/url before pull (dirty/vuln earmarks)")
    aud.add_argument("target")
    aud.add_argument("--trivy", action="store_true")
    aud.add_argument("--docker", action="store_true")
    aud.add_argument("--osv", action="store_true")

    stage_app = sub.add_parser(
        "stage-app",
        help="Stage discovered app as earmark (or --promote proposal)",
    )
    stage_app.add_argument("candidate_id")
    stage_app.add_argument("--promote", action="store_true")
    stage_app.add_argument("--force-earmark", action="store_true")

    smoke = sub.add_parser("smoke", help="T0–T4 smoke scorecard")
    smoke.add_argument(
        "--tiers",
        default="T0,T1,T2,T3,T4",
        help="Comma list e.g. T0,T1 or T0-T4",
    )
    smoke.add_argument("--json", action="store_true")

    lock = sub.add_parser("lock", help="T0–T4 version lock + loading profiles")
    lock_sub = lock.add_subparsers(dest="lock_cmd", required=True)
    lock_sub.add_parser("show", help="Show current lock file")
    lw = lock_sub.add_parser("write", help="Write lock from catalog + git SHAs")
    lw.add_argument("--smoke-ref", default=None)
    ll = lock_sub.add_parser("load", help="Launch loading profile from lock")
    ll.add_argument("profile", help="demo|full_local|video_gpu-host|face|audio|body")
    ll.add_argument("--live", action="store_true")
    ll.add_argument("--monitor", default=None, nargs="?", const="gpu-host")

    mon = sub.add_parser("monitor", help="One-shot gpu-host resource sample")
    mon.add_argument("--node", default="gpu-host")
    mon.add_argument("--json", action="store_true")

    # --- federation: ask packets / nodes / chains ---
    pkt = sub.add_parser("packet", help="ask_packet.v1 emit / award / show")
    pkt_sub = pkt.add_subparsers(dest="packet_cmd", required=True)
    pe = pkt_sub.add_parser("emit", help="Emit packet(s) from story or op")
    pe.add_argument("path", nargs="?", default=None, help="Story markdown/sides (optional)")
    pe.add_argument("--op", default="still", choices=["still", "i2v", "video", "expand", "tts", "face", "stitch"])
    pe.add_argument("--data-class", default="internal", dest="data_class")
    pe.add_argument("--qqq", default="QQQ0")
    pe.add_argument("--allow-crowd", action="store_true")
    pe.add_argument("--duration", type=float, default=5.0)
    pe.add_argument("--max-shots", type=int, default=3)
    pa = pkt_sub.add_parser("award", help="Award packet to best node (dry-run default)")
    pa.add_argument("packet_path")
    pa.add_argument("--live", action="store_true", help="Write award receipt event")
    ps = pkt_sub.add_parser("show", help="Show packet JSON")
    ps.add_argument("packet_path")

    nodes = sub.add_parser("nodes", help="Federation node index (trusted lab)")
    nodes_sub = nodes.add_subparsers(dest="nodes_cmd", required=True)
    nodes_sub.add_parser("list", help="List advertisements")
    ns = nodes_sub.add_parser("seed", help="Seed desk-host/gpu-host/tower from tier_lock")
    ns.add_argument("--force", action="store_true")
    nh = nodes_sub.add_parser("heartbeat", help="Touch last_heartbeat")
    nh.add_argument("node_id")

    ch = sub.add_parser("chains", help="mok-tua-render CHAINS log")
    ch_sub = ch.add_subparsers(dest="chains_cmd", required=True)
    ch_sub.add_parser("verify", help="Verify hash links")
    ch_sub.add_parser("tip", help="Show tip hash / path")

    # --- conductor TUI ---
    tui_p = sub.add_parser(
        "tui",
        help="Full-screen / line TUI over CLI verbs (C64 or modern skin)",
    )
    tui_p.add_argument(
        "--skin",
        choices=["c64", "modern"],
        default="c64",
        help="c64 = PETSCII-style 40-col canvas; modern = navy ops chrome",
    )
    tui_p.add_argument(
        "--repl",
        action="store_true",
        help="Force stdlib line REPL (no Textual)",
    )

    args = p.parse_args()

    if args.cmd == "tui":
        # Ensure repo root on path for `import tui`
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from tui.__main__ import main as tui_main

        argv = ["--skin", args.skin]
        if args.repl:
            argv.append("--repl")
        return tui_main(argv)

    if args.cmd == "inventory":
        import stage_models

        _j(stage_models.inventory_status(manifest_path=args.manifest))
        return 0

    if args.cmd == "stage":
        import stage_models

        out = stage_models.stage_models(
            manifest_path=args.manifest,
            dry_run=not args.live,
            only_ids=args.only,
            required_for=args.required_for or None,
        )
        _j(out)
        return 0 if out.get("ok") else 1

    if args.cmd == "sides":
        from sides_ingest import ingest_sides_file
        import stages

        r = ingest_sides_file(args.path)
        if not r.get("ok"):
            _j(r)
            return 1
        if args.out:
            Path(args.out).write_text(r["markdown"], encoding="utf-8")
            print(f"wrote {args.out}")
        if args.run:
            dry = not args.no_dry_run and not args.live_still
            r["run"] = stages.create_run_from_markdown(
                r["markdown"],
                dry_run=dry,
                live_still=args.live_still,
                still_provider=args.still_provider,
            )
            _j({
                "ok": True,
                "format": r.get("format"),
                "title": r.get("title"),
                "run_id": r["run"].get("run_id"),
                "shot_count": r["run"].get("shot_count"),
                "still_provider": r["run"].get("still_provider"),
                "run_dir": r["run"].get("run_dir"),
            })
        elif not args.out:
            print(r["markdown"][:4000])
        return 0

    if args.cmd == "run":
        import stages
        from sides_ingest import ingest_sides_file

        path = Path(args.path)
        if path.suffix.lower() in (".pdf", ".fdx", ".txt"):
            ing = ingest_sides_file(path)
            if not ing.get("ok"):
                _j(ing)
                return 1
            text = ing["markdown"]
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
        dry = not args.no_dry_run and not args.live_still
        state = stages.create_run_from_markdown(
            text,
            dry_run=dry,
            live_still=args.live_still,
            still_provider=args.still_provider,
            video_provider=args.video_provider,
            qqq=args.qqq,
        )
        _j({
            "run_id": state.get("run_id"),
            "shot_count": state.get("shot_count"),
            "still_provider": state.get("still_provider"),
            "video_provider": state.get("video_provider"),
            "dry_run": state.get("dry_run"),
            "run_dir": state.get("run_dir"),
        })
        return 0

    if args.cmd == "batch":
        import stages
        from sides_ingest import ingest_sides_file

        dry = not args.no_dry_run and not args.live_still
        results = []
        for path in args.paths:
            pth = Path(path)
            if pth.suffix.lower() in (".pdf", ".fdx", ".txt", ".md", ".markdown"):
                ing = ingest_sides_file(pth)
                if not ing.get("ok"):
                    results.append({"path": path, "ok": False, "error": ing.get("error")})
                    continue
                md = ing["markdown"]
            else:
                md = pth.read_text(encoding="utf-8", errors="replace")
            state = stages.create_run_from_markdown(
                md,
                dry_run=dry,
                live_still=args.live_still,
                still_provider=args.still_provider,
            )
            results.append({
                "path": path,
                "ok": True,
                "run_id": state.get("run_id"),
                "shot_count": state.get("shot_count"),
                "still_provider": state.get("still_provider"),
            })
        _j({"ok": all(r.get("ok") for r in results), "runs": results})
        return 0

    if args.cmd == "providers":
        import providers

        out = providers.list_providers(
            tier=args.tier,
            role=args.role,
            bleeding_only=args.bleed,
            probe=not args.no_probe,
        )
        if args.json:
            _j(out)
        else:
            print(providers.format_table(out["providers"]))
            print(f"\nlive {out['live']}/{out['count']}  ·  ai-data {out['ai_data']}")
        return 0

    if args.cmd == "doctor":
        import providers

        out = providers.doctor()
        if args.json:
            _j(out)
        else:
            print(f"mok-tua doctor  grade={out.get('grade')}  score={out.get('score')}/{out.get('max_score')}")
            print(f"defaults: {out.get('defaults')}")
            print("critical:")
            for k, v in (out.get("critical") or {}).items():
                print(f"  {k:<20} live={v.get('live')} path={v.get('path_ok')} open={v.get('open')}")
            mi = out.get("model_inventory") or {}
            print(f"models: present={mi.get('present')} failed={mi.get('failed')} count={mi.get('count')}")
            print(f"providers live={out.get('providers_live')}/{out.get('providers_count')}")
        return 0

    if args.cmd == "status":
        import providers

        prov = providers.list_providers(probe=True)
        doc = providers.doctor()
        if args.json:
            _j({"providers": prov, "doctor": doc})
        else:
            print(providers.format_table(prov["providers"]))
            print(f"\ngrade {doc.get('grade')}  live {prov['live']}/{prov['count']}")
        return 0

    if args.cmd == "launch":
        import providers

        target = args.target
        chains = {"demo", "video", "face", "audio", "body", "full"}
        dry = not args.live
        if target in chains:
            out = providers.launch_chain(target, dry_run=dry)
        else:
            out = providers.launch_provider(
                target, dry_run=dry, force=args.force, port=args.port
            )
        if args.json or dry:
            _j(out)
        else:
            _j(out)
            if out.get("open"):
                print(f"\nopen → {out['open']}")
            if out.get("log"):
                print(f"log  → {out['log']}")
        return 0 if out.get("ok") else 1

    if args.cmd == "stop":
        import providers

        _j(providers.stop_provider(args.provider_id))
        return 0

    if args.cmd == "pull":
        import providers
        from host_monitor import run_with_monitor

        dry = not args.live
        mon = args.monitor if args.live else None

        if args.all_bleed or args.tier:
            def _bulk():
                return providers.pull_tier(
                    tier=args.tier,
                    bleeding_only=args.all_bleed and not args.tier,
                    dry_run=dry,
                    monitor=None,  # outer monitor when live
                    force=args.force,
                    priority_max=args.priority_max,
                )

            if mon:
                out, mon_sum = run_with_monitor(_bulk, node=mon, label="pull")
                if isinstance(out, dict):
                    out["monitor_outer"] = mon_sum
            else:
                # pull_tier starts its own monitor if monitor set; pass mon for live
                out = providers.pull_tier(
                    tier=args.tier,
                    bleeding_only=bool(args.all_bleed and not args.tier),
                    dry_run=dry,
                    monitor=mon,
                    force=args.force,
                    priority_max=args.priority_max,
                )
            _j(out)
            return 0 if out.get("ok") or out.get("skipped") else 1

        if not args.provider_id:
            print("pull requires provider_id or --tier / --all-bleed", file=sys.stderr)
            return 2

        def _one():
            return providers.pull_provider(
                args.provider_id, dry_run=dry, force=args.force
            )

        if mon:
            out, mon_sum = run_with_monitor(
                _one, node=mon, label=f"pull:{args.provider_id}"
            )
            if isinstance(out, dict):
                out["monitor"] = mon_sum
        else:
            out = _one()
        _j(out)
        return 0 if out.get("ok") else 1

    if args.cmd == "discover":
        import discover_audit

        out = discover_audit.discover(source=args.source, limit=args.limit)
        if args.json:
            _j(out)
        else:
            print(f"discover count={out['count']} sources={out['sources']}")
            for c in out.get("candidates") or []:
                print(
                    f"  {c.get('id') or '':<28} {c.get('source') or '':<16} "
                    f"{c.get('path') or c.get('url') or ''}"
                )
        return 0

    if args.cmd == "audit":
        import discover_audit

        _j(
            discover_audit.audit(
                args.target,
                trivy=args.trivy,
                docker=args.docker,
                osv=args.osv,
            )
        )
        return 0

    if args.cmd == "stage-app":
        import discover_audit

        out = discover_audit.stage_candidate(
            args.candidate_id,
            promote=args.promote,
            force_earmark=args.force_earmark,
        )
        _j(out)
        return 0 if out.get("ok") else 1

    if args.cmd == "smoke":
        import smoke_tiers

        tiers_raw = args.tiers.replace("T0-T4", "T0,T1,T2,T3,T4")
        tiers = [t.strip() for t in tiers_raw.split(",") if t.strip()]
        report = smoke_tiers.run_smoke(tiers)
        if args.json:
            _j(report)
        else:
            print(smoke_tiers.format_smoke_table(report))
        return 0 if report.get("ok") else 1

    if args.cmd == "lock":
        import tier_lock

        if args.lock_cmd == "show":
            out = tier_lock.load_lock()
            _j(out)
            return 0 if out.get("ok") else 1
        if args.lock_cmd == "write":
            out = tier_lock.write_lock(smoke_ref=args.smoke_ref)
            _j({"ok": out.get("ok"), "path": out.get("path"), "version": (out.get("lock") or {}).get("mok_tua_version")})
            return 0 if out.get("ok") else 1
        if args.lock_cmd == "load":
            out = tier_lock.load_profile(
                args.profile,
                dry_run=not args.live,
                monitor=args.monitor if args.live else None,
            )
            _j(out)
            return 0 if out.get("ok") else 1
        return 2

    if args.cmd == "monitor":
        from host_monitor import format_sample_line, sample_host

        s = sample_host(args.node)
        if args.json:
            _j(s)
        else:
            print(format_sample_line(s))
            _j(s)
        return 0 if s.get("ok") else 1

    if args.cmd == "packet":
        import ask_packet
        import award

        if args.packet_cmd == "emit":
            try:
                if args.path:
                    text = Path(args.path).read_text(encoding="utf-8", errors="replace")
                    # sides?
                    if Path(args.path).suffix.lower() in (".pdf", ".fdx", ".txt"):
                        from sides_ingest import ingest_sides_file

                        ing = ingest_sides_file(args.path)
                        if not ing.get("ok"):
                            _j(ing)
                            return 1
                        text = ing["markdown"]
                    out = ask_packet.emit_from_story_markdown(
                        text,
                        data_class=args.data_class,
                        qqq_floor=args.qqq,
                        allow_crowd=args.allow_crowd,
                        max_shots=args.max_shots,
                    )
                else:
                    pkt_one = ask_packet.emit_packet(
                        op=args.op,
                        duration_s=args.duration,
                        data_class=args.data_class,
                        qqq_floor=args.qqq,
                        allow_crowd=args.allow_crowd,
                    )
                    out = {"ok": True, "count": 1, "packets": [pkt_one]}
            except ValueError as exc:
                _j({"ok": False, "error": str(exc)})
                return 1
            # strip huge nested for display
            slim = {
                "ok": out.get("ok"),
                "title": out.get("title"),
                "count": out.get("count"),
                "packets": [
                    {
                        "id": p.get("id"),
                        "path": p.get("_path"),
                        "lock_ref": (p.get("manifest") or {}).get("lock_ref"),
                        "op": (p.get("manifest") or {}).get("op"),
                        "data_class": (p.get("manifest") or {}).get("data_class"),
                        "qqq_floor": (p.get("manifest") or {}).get("qqq_floor"),
                        "expect": (p.get("manifest") or {}).get("expect"),
                    }
                    for p in (out.get("packets") or [])
                ],
            }
            _j(slim)
            return 0

        if args.packet_cmd == "show":
            data = json.loads(Path(args.packet_path).read_text(encoding="utf-8"))
            _j(data)
            return 0

        if args.packet_cmd == "award":
            data = json.loads(Path(args.packet_path).read_text(encoding="utf-8"))
            res = award.award_packet(data, dry_run=not args.live)
            _j(res)
            return 0 if res.get("ok") else 1
        return 2

    if args.cmd == "nodes":
        import crowd_index

        if args.nodes_cmd == "list":
            _j(crowd_index.list_nodes())
            return 0
        if args.nodes_cmd == "seed":
            _j(crowd_index.seed_lab_nodes(force=args.force))
            return 0
        if args.nodes_cmd == "heartbeat":
            _j(crowd_index.heartbeat(args.node_id))
            return 0
        return 2

    if args.cmd == "chains":
        import chains_render

        if args.chains_cmd == "verify":
            _j(chains_render.verify_chain())
            return 0
        if args.chains_cmd == "tip":
            _j(
                {
                    "chain_id": chains_render.CHAIN_ID,
                    "tip": chains_render.last_hash(),
                    "path": str(chains_render.chain_path()),
                }
            )
            return 0
        return 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
