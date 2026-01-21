"""
OAuth 第三方登录测试脚本
用于验证 OAuth 配置和功能
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth.third_party_login import get_available_providers, get_oauth_config
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_oauth_config():
    """测试 OAuth 配置"""
    print("=" * 60)
    print("OAuth 第三方登录配置测试")
    print("=" * 60)

    # 获取可用的提供商
    providers = get_available_providers()

    print(f"\n可用的 OAuth 提供商（共 {len(providers)} 个）：")
    print("-" * 60)

    if not providers:
        print("❌ 没有配置任何 OAuth 提供商")
        print("\n请在 .env 文件中配置以下变量（至少一个）：")
        print("  - GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET / GITHUB_REDIRECT_URI")
        print("  - QQ_CLIENT_ID / QQ_CLIENT_SECRET / QQ_REDIRECT_URI")
        print("  - WECHAT_CLIENT_ID / WECHAT_CLIENT_SECRET / WECHAT_REDIRECT_URI")
        return

    for provider in providers:
        print(f"✅ {provider['name']} ({provider['provider']})")
        config = get_oauth_config(provider["provider"])
        if config:
            print(
                f"   - Client ID: {config['client_id'][:20]}..."
                if config["client_id"]
                else "   - Client ID: (未配置)"
            )
            print(f"   - Redirect URI: {config['redirect_uri']}")
        print()

    print("\n" + "=" * 60)
    print("配置检查完成")
    print("=" * 60)


def test_redirect_uris():
    """测试回调 URI 配置"""
    print("\n" + "=" * 60)
    print("回调 URI 配置检查")
    print("=" * 60)

    providers = ["github", "gitee", "qq", "wechat", "google"]

    for provider in providers:
        config = get_oauth_config(provider)
        if config:
            redirect_uri = config.get("redirect_uri", "")
            if redirect_uri:
                print(f"\n{provider.upper()}:")
                print(f"  回调地址: {redirect_uri}")

                # 检查回调地址格式
                if redirect_uri.startswith("http://localhost"):
                    print(f"  ⚠️  开发环境，生产环境请使用 HTTPS")
                elif redirect_uri.startswith("https://"):
                    print(f"  ✅ 生产环境")
                else:
                    print(f"  ❌ 回调地址格式不正确")
            else:
                print(f"\n{provider.upper()}:")
                print(f"  ❌ 未配置回调地址")


if __name__ == "__main__":
    test_oauth_config()
    test_redirect_uris()

    print("\n提示：")
    print("1. 确保 .env 文件中配置了正确的 Client ID 和 Secret")
    print("2. 确保第三方平台的回调地址与配置一致")
    print("3. 启动后端服务后，访问 /auth/oauth/providers 查看可用平台")
