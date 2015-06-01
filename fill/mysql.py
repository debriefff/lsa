create_sql = '''
CREATE TABLE `documents` (
    `id` int(11) NOT NULL,
    `title` varchar(255) COLLATE utf8_bin NOT NULL,
    `content` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
'''

import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             passwd='23021993',
                             db='docs',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.Cursor)

from fill import source

try:
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS documents")
        cursor.execute(create_sql)


        i = 0
        for doc in source.docs:
            # Create a new record
            sql = "INSERT INTO `documents` (`id`, `title`, `content`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (i, 'title %s' % i, doc))
            i += 1

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * FROM `documents`;"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
finally:
    connection.close()

print('Ready.')