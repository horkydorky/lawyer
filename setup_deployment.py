#!/usr/bin/env python3
"""
Setup script to configure deployment files for MyPocketLawyer
"""

def update_render_yaml():
    print("=" * 60)
    print("MyPocketLawyer - Deployment Configuration")
    print("=" * 60)
    print()
    
    # Get user input
    github_username = input("Enter your GitHub username: ").strip()
    repo_name = input("Enter your repository name: ").strip()
    
    if not github_username or not repo_name:
        print("❌ Error: Username and repository name are required!")
        return
    
    github_url = f"https://github.com/{github_username}/{repo_name}"
    
    # Read render.yaml
    try:
        with open('render.yaml', 'r') as f:
            content = f.read()
        
        # Replace placeholder
        updated_content = content.replace(
            'repo: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME',
            f'repo: {github_url}'
        )
        
        # Write back
        with open('render.yaml', 'w') as f:
            f.write(updated_content)
        
        print()
        print("✅ render.yaml updated successfully!")
        print(f"   Repository URL: {github_url}")
        print()
        print("Next steps:")
        print("1. Commit and push to GitHub:")
        print(f"   git add render.yaml")
        print(f"   git commit -m 'Update render.yaml with repository URL'")
        print(f"   git push")
        print()
        print("2. Go to https://dashboard.render.com/")
        print("3. Click 'New +' → 'Blueprint'")
        print("4. Connect your GitHub repository")
        print("5. Add GEMINI_API_KEY environment variable")
        print("6. Click 'Apply'")
        print()
        
    except FileNotFoundError:
        print("❌ Error: render.yaml not found!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_render_yaml()
