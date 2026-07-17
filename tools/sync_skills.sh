#!/usr/bin/env bash
#
# sync_skills.sh — 把 PersonOS skills 的唯一源 (.agents/skills/) 同步到各部署副本。
#
#   源 (source of truth) : <repo>/.agents/skills/<name>/
#   目标 1 (Codex 运行副本): ~/.codex/skills/<name>/        (SKILL.md 里 run 路径指向这里)
#   目标 2 (可分发 skill 包): <repo>/<name>.skill.zip        (供 Claude Cowork 重新导入)
#
# 用法：
#   bash tools/sync_skills.sh              # 同步到 Codex + 重新打包 zip
#   bash tools/sync_skills.sh --dry-run    # 只预览 rsync 差异，不写任何东西
#   bash tools/sync_skills.sh --codex-only # 只同步 Codex 副本
#   bash tools/sync_skills.sh --zip-only   # 只重新打包 .skill.zip
#   CODEX_SKILLS=/自定义/路径 bash tools/sync_skills.sh   # 覆盖 Codex 目标目录
#
# 注意：在 macOS 上请从「终端」运行，并确保终端已获「完全磁盘访问权限」，
#       否则访问 ~/Documents 或 ~/.codex 可能被 TCC 拦截。
set -euo pipefail

# 定位仓库根目录（本脚本位于 <repo>/tools/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO/.agents/skills"
CODEX_DEST="${CODEX_SKILLS:-$HOME/.codex/skills}"

DRY_RUN=0
DO_CODEX=1
DO_ZIP=1
for arg in "$@"; do
  case "$arg" in
    --dry-run)   DRY_RUN=1 ;;
    --codex-only) DO_ZIP=0 ;;
    --zip-only)  DO_CODEX=0 ;;
    -h|--help)   sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "未知参数：$arg" >&2; exit 2 ;;
  esac
done

[ -d "$SRC" ] || { echo "找不到源目录：$SRC" >&2; exit 1; }

# 需要从同步和打包中排除的垃圾
EXCLUDES=(--exclude '__pycache__' --exclude '*.pyc' --exclude '.DS_Store')

echo "仓库根 : $REPO"
echo "源目录 : $SRC"
[ "$DO_CODEX" = 1 ] && echo "Codex  : $CODEX_DEST"
[ "$DO_ZIP" = 1 ]   && echo "zip 包 : $REPO/<name>.skill.zip"
echo "----------------------------------------"

changed=0
for dir in "$SRC"/*/; do
  name="$(basename "$dir")"
  [ -f "$dir/SKILL.md" ] || { echo "跳过 $name（缺 SKILL.md）"; continue; }
  echo "» $name"

  # 目标 1：Codex 运行副本（镜像同步，--delete 清掉源里已删除的文件）
  if [ "$DO_CODEX" = 1 ]; then
    mkdir -p "$CODEX_DEST/$name"
    if [ "$DRY_RUN" = 1 ]; then
      rsync -a -n -i --delete "${EXCLUDES[@]}" "$dir" "$CODEX_DEST/$name/" || true
    else
      rsync -a --delete "${EXCLUDES[@]}" "$dir" "$CODEX_DEST/$name/"
      echo "  ✓ 已同步到 $CODEX_DEST/$name/"
    fi
  fi

  # 目标 2：重新打包 <name>.skill.zip（SKILL.md 位于包内根层）
  if [ "$DO_ZIP" = 1 ]; then
    zip_path="$REPO/$name.skill.zip"
    if [ "$DRY_RUN" = 1 ]; then
      echo "  (dry-run) 将重建 $zip_path"
    else
      rm -f "$zip_path"
      ( cd "$dir" && zip -r -q -X "$zip_path" . \
          -x '*/__pycache__/*' -x '*.pyc' -x '.DS_Store' -x '*/.DS_Store' )
      echo "  ✓ 已重建 $(basename "$zip_path")"
    fi
  fi
  changed=$((changed+1))
done

echo "----------------------------------------"
if [ "$DRY_RUN" = 1 ]; then
  echo "dry-run 完成：共 $changed 个 skill（未写入任何文件）"
else
  echo "完成：处理了 $changed 个 skill"
  [ "$DO_ZIP" = 1 ] && echo "提示：Claude Cowork 侧需在 设置 › Capabilities 重新导入更新后的 .skill.zip"
fi
