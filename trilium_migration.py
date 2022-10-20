import sqlite3 as sql

"""
Transfer data from a Trilium Notes v0.45.8 document.db database to a newly generated
Trilium Notes v0.55.1 document.db database

Note: we do not transfer the api_keys, entity_changes, options, or sqlite_sequence
tables because they did not need to be transfered for my use case.
Also they were hard to transfer.
"""

# constants
OLD_DB = "document-old.db"  # file path for the 0.45.8 document.db file
NEW_DB = "document-new.db"  # file path for the 0.55.1 document.db file

# transfer masks: 0's denote columns to drop from the old database
ATTRIBUTES_TM = (1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1)  # for table 'attributes'
BRANCHES_TM = (1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0)  # for table 'branches'
NOTE_CONTENTS_TM = (1, 1, 0, 1, 1)  # for table 'note_contents'
NOTE_REVISION_CONTENTS_TM = (1, 1, 0, 1)  # for table 'note_revision_contents'
NOTES_TM = (1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1)  # for table 'notes'
RECENT_NOTES_TM = (1, 1, 0, 1, 0)  # for table 'recent_notes'


def insert_rows(rows, table, cursor):
    """insert rows into a given table"""
    numCols = len(rows[0])
    placeholder = "(" + ("?, " * (numCols - 1)) + "?)"
    insertQuery = f"INSERT INTO {table} VALUES{placeholder};"
    cursor.executemany(insertQuery, rows)
    print(f"\nInserted {len(rows)} rows into table {table} in {NEW_DB}\n")


def transfer_table(tableName, transferMask, oldCursor, newCursor):
    """transfer all data from a table in the old database to a table in the
    new database with the same name, skip collisions"""
    selectQuery = f"SELECT * FROM {tableName};"

    oldData = oldCursor.execute(selectQuery).fetchall()
    print(f"\nFetched {len(oldData)} records from table {tableName} in {OLD_DB}")
    newData = newCursor.execute(selectQuery).fetchall()
    print(f"Fetched {len(newData)} records from table {tableName} in {NEW_DB}\n")

    # skip any row with the same id
    newUIDs = set([row[0] for row in newData])
    rowsToTransfer = []
    for row in oldData:
        if row[0] in newUIDs:
            print("Skipping row with UID " + row[0] + " in table " + tableName)
        else:
            transferableRow = tuple(
                [val for val, maskVal in zip(row, transferMask) if maskVal]
            )
            rowsToTransfer.append(transferableRow)

    # insert rows into new database
    insert_rows(rowsToTransfer, tableName, newCursor)


def transfer_revisions_table(oldCursor, newCursor):
    """transfer the revisions table because it's weird but we need it"""
    selectQuery = "SELECT noteRevisionId, noteId, type, mime, title, isProtected, utcDateLastEdited, utcDateCreated, utcDateModified, dateLastEdited, dateCreated FROM note_revisions;"

    oldData = oldCursor.execute(selectQuery).fetchall()
    print(f"\nFetched {len(oldData)} records from table note_revisions in {OLD_DB}")
    newData = newCursor.execute(selectQuery).fetchall()
    print(f"Fetched {len(newData)} records from table note_revisions in {NEW_DB}\n")

    # skip any row with the same id
    newUIDs = set([row[0] for row in newData])
    rowsToTransfer = []
    for row in oldData:
        if row[0] in newUIDs:
            print("Skipping row with UID " + row[0] + " in table " + tableName)
        else:

            # handle null titles from old version
            if row[4] in ("", None):
                row = list(row)
                row[4] = "No Title"
                row = tuple(row)
            rowsToTransfer.append(row)

    # insert rows into new database
    insert_rows(rowsToTransfer, "note_revisions", newCursor)


def main():
    oldCon = sql.connect(OLD_DB)
    newCon = sql.connect(NEW_DB)
    oldCursor = oldCon.cursor()
    newCursor = newCon.cursor()

    # map table names to their transfer masks
    maskMap = [
        ("attributes", ATTRIBUTES_TM),
        ("branches", BRANCHES_TM),
        ("note_contents", NOTE_CONTENTS_TM),
        ("note_revision_contents", NOTE_REVISION_CONTENTS_TM),
        ("notes", NOTES_TM),
        ("recent_notes", RECENT_NOTES_TM),
    ]

    # transfer tables according to their transfer masks
    for tableName, transferMap in maskMap:
        transfer_table(tableName, transferMap, oldCursor, newCursor)
        newCon.commit()

    # transfer the note revisions table
    transfer_revisions_table(oldCursor, newCursor)
    newCon.commit()

    # could we use a with statement instead of explicitly closing?
    oldCon.close()
    newCon.close()


if __name__ == "__main__":
    main()
