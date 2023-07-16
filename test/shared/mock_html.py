# pylint: skip-file


def get_html():
    return """
    <html>
        <body>
            <table>
                <ul>
                    <li><a href='http://address.com/seller/ali' id='100'>Link 1</a></li>
                    <li><a href='http://address.com/seller/gholi' id='200'>Link 2</a></li>
                    <li><a href='http://address.com/seller/abbas' id='300'>Link 3</a></li>
                </ul>
            </table>
            <nav>
                <ul class="pagination">
                    <li><a href="http://address.com/item?page=1" class="active">1</a></li>
                    <li><a href="http://address.com/item?page=2">2</a></li>
                    <li><a href="http://address.com/item?page=3">3</a></li>
                </ul>
            </nav>
        </body>
    </html>
    """


def get_corrupted_html():
    return """
    <html>
        <body>
            <table>
                <ul>
                    <li><a href='http://address.com/seller/ali' id='aa100'>Link 1</a></li>
                    <li><a href='http://address.com/seller/gholi' id='bb200'>Link 2</a></li>
                    <li><a href='http://address.com/seller/abbas' id='cc300'>Link 3</a></li>
                </ul>
            </table>
            <nav>
                <ul class="pagination">
                    <li><a href="http://address.com/item?page=1" class="active">1</a></li>
                    <li><a href="http://address.com/item?page=2">2</a></li>
                    <li><a href="http://address.com/item?page=3">3</a></li>
                </ul>
            </nav>
        </body>
    </html>
    """
