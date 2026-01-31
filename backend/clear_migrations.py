"""清除Django应用的迁移文件"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def get_apps():
    """获取所有Django应用列表"""
    apps = []
    for item in BASE_DIR.iterdir():
        if item.is_dir() and (item / 'migrations').exists():
            apps.append(item.name)
    return sorted(apps)


def clear_migrations(app_name=None):
    """清除指定应用的迁移文件"""
    if not app_name:
        apps = get_apps()
        if not apps:
            print("未找到任何带有migrations目录的应用")
            return

        print("可用应用:")
        for i, app in enumerate(apps, 1):
            print(f"  {i}. {app}")

        choice = input("\n请选择应用编号: ")
        try:
            app_name = apps[int(choice) - 1]
        except (ValueError, IndexError):
            print("无效选择")
            return

    migrations_dir = BASE_DIR / app_name / 'migrations'

    if not migrations_dir.exists():
        print(f"应用 {app_name} 的迁移目录不存在")
        return

    files_to_delete = []
    for file in migrations_dir.iterdir():
        if file.is_file() and file.name != '__init__.py' and file.name.endswith('.py'):
            files_to_delete.append(file)

    if not files_to_delete:
        print(f"应用 {app_name} 没有迁移文件")
        return

    print(f"\n将清除应用 {app_name} 的以下迁移文件:")
    for file in files_to_delete:
        print(f"  - {file.name}")

    confirm = input("\n确认删除? (y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return

    for file in files_to_delete:
        file.unlink()
        print(f"已删除: {file.name}")

    print("\n迁移文件已清除")
    print("请运行以下命令重新生成迁移:")
    print(f"  python manage.py makemigrations {app_name}")
    print(f"  python manage.py migrate {app_name} --fake")


def clear_all_migrations():
    """一键清除所有应用的迁移文件"""
    apps = get_apps()

    if not apps:
        print("未找到任何带有migrations目录的应用")
        return

    all_files = {}
    total_count = 0

    for app_name in apps:
        migrations_dir = BASE_DIR / app_name / 'migrations'
        files_to_delete = []
        for file in migrations_dir.iterdir():
            if file.is_file() and file.name != '__init__.py' and file.name.endswith('.py'):
                files_to_delete.append(file)
        if files_to_delete:
            all_files[app_name] = files_to_delete
            total_count += len(files_to_delete)

    if not all_files:
        print("所有应用都没有迁移文件")
        return

    print(f"将清除以下 {total_count} 个迁移文件:")
    for app_name, files in all_files.items():
        print(f"\n{app_name}:")
        for file in files:
            print(f"  - {file.name}")

    confirm = input("\n确认删除? (y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return

    deleted_count = 0
    for app_name, files in all_files.items():
        for file in files:
            file.unlink()
            deleted_count += 1

    print(f"\n已清除 {deleted_count} 个迁移文件")
    print("请运行以下命令重新生成迁移:")
    print("  python manage.py makemigrations")
    print("  python manage.py migrate --fake")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ('-a', '--all'):
            clear_all_migrations()
        else:
            clear_migrations(arg)
    else:
        clear_migrations()


if __name__ == '__main__':
    main()
