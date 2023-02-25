from typing import Optional
from fastapi import Depends, Response, status, HTTPException, APIRouter
from pydantic import BaseModel
from psycopg2.errorcodes import UNIQUE_VIOLATION
from ..database import cursor, conn
from .. import oauth2

router = APIRouter(
    tags=['Posts']
)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
    user_id: int


class CreatePost(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None




@router.get("/posts")
def get_posts(current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""
    SELECT posts.*, COUNT(votes.post_id) AS votes FROM posts 
    LEFT JOIN votes 
    ON votes.post_id = posts.id
    GROUP BY posts.id
    """)
    posts = cursor.fetchall()
    
    
    return {"data": posts}


@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: CreatePost,
current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""
    INSERT INTO posts (title, content, published, user_id, user_email)
    VALUES (%s, %s, %s, %s, %s) RETURNING *
    """, (post.title, post.content, post.published, current_user['id'],
    current_user['email'],))

    new_post = cursor.fetchone()
    
    conn.commit()
    return {"data": new_post}



#path parameter {id}
@router.get("/posts/{id}")
def get_post(id: int,
current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""
    SELECT posts.*, COUNT(votes.post_id) AS votes FROM posts 
    LEFT JOIN votes 
    ON votes.post_id = posts.id
    WHERE id = %s
    GROUP BY posts.id
    """, str(id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} not found")

    
    return {"post_detail": post}





@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,
current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""
    SELECT * FROM posts WHERE id = %s
    """, str(id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} not found")

    if post['user_id'] != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail = f"post with id: {id} is not yours")

    cursor.execute("""
    DELETE FROM posts WHERE id = %s RETURNING *
    """, (str(id),))
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.put("/posts/{id}")
def update_post(id: int, post: CreatePost,
current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""
    SELECT * FROM posts WHERE id = %s
    """, str(id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} not found")

    if post['user_id'] != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail = f"post with id: {id} is not yours")


    cursor.execute("""
    UPDATE posts 
    SET title = (%s), content = (%s), published = (%s)
    WHERE id = %s RETURNING *
    """, (post.title, post.content, post.published, str(id),))
    conn.commit()
    post_dict = cursor.fetchone()
    if not post_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} does not exist")
    return {'data': post_dict}





