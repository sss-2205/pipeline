
# from app.db.supabase_client import supabase

# def get_cached_article(url: str):
    

#     res = supabase.table("article_with_score") \
#         .select("*") \
#         .eq("url", url) \
#         .limit(1) \
#         .execute()
#     if res.data:
#         if res.data[0]['bias_score'] is not None:
#             return (True,res.data[0])
    
#         else:
#             article_id = res.data[0]['article_id']
#             return (False, article_id)
#     else:
#         return (False, None)




from app.db.supabase_client import supabase

# def get_cached_article(url: str):
#     try:
#         print("🔍 Checking cache for URL:", url)

#         res = supabase.table("article_with_score") \
#             .select("*") \
#             .eq("url", url) \
#             .limit(1) \
#             .execute()

#         print("✅ Supabase response received")
#         print("DATA:", res.data)
#         print("ERROR:", res.error if res.error else "None")

#         if res.data:
#             if res.data[0]['bias_score'] is not None:
#                 return (True, res.data[0])
#             else:
#                 article_id = res.data[0]['article_id']
#                 return (False, article_id)
#         else:
#             return (False, None)

#     except Exception as e:
#         print("❌ ERROR in get_cached_article:", str(e))
#         return (False, None)
    

def get_cached_article(url: str):
    try:
        res = supabase.table("article_with_score") \
            .select("*") \
            .eq("url", url) \
            .limit(1) \
            .execute()

        print("DATA:", res.data)

        if res.data:
            row = res.data[0]

            if row.get('bias_score') is not None:
                return (True, row)   # fully cached
            else:
                return (False, row)  # exists but not processed

        else:
            return (False, None)     # new article

    except Exception as e:
        print("ERROR:", str(e) or res.error)
        return (False, None)