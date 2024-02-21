from db_client import chat_exists  # Adjust the import path if necessary

# Example chat IDs - replace these with actual IDs from your database
existing_chat_id = "65ca1e4c448e0919f019c522"  # Update this with a valid chat_id from your DB
non_existing_chat_id = "5f77682e4d2f4a3f62c465b8"  # Use an invalid chat_id

def test_chat_exists():
    print(f"Testing with existing chat ID: {existing_chat_id}")
    if chat_exists(existing_chat_id):
        print("✅ Existing chat ID test passed.")
    else:
        print("❌ Existing chat ID test failed.")

    print(f"\nTesting with non-existing chat ID: {non_existing_chat_id}")
    if chat_exists(non_existing_chat_id):
        print("❌ Non-existing chat ID test failed.")
    else:
        print("✅ Non-existing chat ID test passed.")

if __name__ == "__main__":
    test_chat_exists()
