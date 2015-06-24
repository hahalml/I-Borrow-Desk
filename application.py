from database_access import initialize_dbase, update_borrow, \
    tight_borrow, ftp_update, create_user, get_user_id, insert_watchlist, get_watchlist, remove_watchlist, summary_report



#ftp_update()
# initialize_dbase()

# update_db()


# print tight_borrow(500)

# print create_user("cmochrie", "test@gmail.com")
#print get_user_id("test@gmail.com")

print insert_watchlist(1, ["BAC", "C", "ANY", "IBM", "CRM"])
remove_watchlist(1, ["C", "CRM", "alsgdasdg"])
print get_watchlist(1)
print summary_report(get_watchlist(1))
#print get_watchlist(1)



