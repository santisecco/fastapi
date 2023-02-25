from fastapi import Depends, Response, status, HTTPException, APIRouter
from pydantic import BaseModel
from .. import database, oauth2

class Vote(BaseModel):
    post_id: int
    dir: bool

router = APIRouter(
    tags=['Vote']
)


@router.post("/vote")
def vote(vote: Vote, current_user: int = Depends(oauth2.get_current_user)):
    if(vote.dir):
        database.cursor.execute("""
            DELETE FROM votes 
            WHERE post_id = %s AND user_id = %s
            RETURNING *
            """, (vote.post_id, current_user['id'],))

        vote_returned = database.cursor.fetchone()

        if vote_returned is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail = f"Already voted this post")

        database.cursor.execute("""
            INSERT INTO votes (post_id, user_id)
            VALUES (%s, %s) RETURNING *
            """, (vote.post_id, current_user['id'],))
        
        vote_returned = database.cursor.fetchone()

        if not vote_returned:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail = f"post not found")
        database.conn.commit()

    else:
        database.cursor.execute("""
            DELETE FROM votes 
            WHERE post_id = %s AND user_id = %s
            RETURNING *
            """, (vote.post_id, current_user['id'],))

        unvote_returned = database.cursor.fetchone()

        if not unvote_returned:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail = f"vote not found")

        database.conn.commit()

    return {"data": vote}