# AI Blog Writer & SEO Agent — 100 QA Test Cases

---

## CATEGORY 1: Blog Generation API (15 test cases)

### TC-001 | Blog Generation API | Valid topic generates blog successfully
**Precondition**: AI API key is set and valid; database is empty
**Steps**:
  1. POST /api/blogs/generate with body `{"topic": "How to Scale a SaaS Product"}`
  2. Wait for response (expected 10–30 seconds)
  3. Verify response contains post ID, outline sections, and content
**Expected Result**: HTTP 201; response has `{id, topic, title, content, outline: {sections: [...]}, seo_score, status: "generated"}`
**Test Type**: Integration
**Priority**: High
**Note**: AI-dependent; mock with fixed response in CI/CD

---

### TC-002 | Blog Generation API | Empty topic string returns 422
**Precondition**: Valid API request setup
**Steps**:
  1. POST /api/blogs/generate with body `{"topic": ""}`
  2. Capture response
**Expected Result**: HTTP 422; error message includes "topic" field requirement
**Test Type**: Unit
**Priority**: High

---

### TC-003 | Blog Generation API | Topic under 5 characters returns 422
**Precondition**: Valid API request setup
**Steps**:
  1. POST /api/blogs/generate with body `{"topic": "AI"}`
  2. Capture response
**Expected Result**: HTTP 422; error message "topic must be at least 5 characters"
**Test Type**: Unit
**Priority**: High

---

### TC-004 | Blog Generation API | Topic exactly 512 characters succeeds
**Precondition**: Valid API request setup; topic string of exactly 512 chars prepared
**Steps**:
  1. POST /api/blogs/generate with max-length topic
  2. Capture response
**Expected Result**: HTTP 201; post created successfully
**Test Type**: Unit
**Priority**: Medium

---

### TC-005 | Blog Generation API | Topic exceeding 512 characters returns 422
**Precondition**: Valid API request setup; topic string of 513 chars prepared
**Steps**:
  1. POST /api/blogs/generate with oversized topic
  2. Capture response
**Expected Result**: HTTP 422; error message "topic must not exceed 512 characters"
**Test Type**: Unit
**Priority**: Medium

---

### TC-006 | Blog Generation API | Topic with emoji characters succeeds
**Precondition**: Valid API request setup
**Steps**:
  1. POST /api/blogs/generate with body `{"topic": "SEO Tips 🚀 for 2026"}`
  2. Capture response
**Expected Result**: HTTP 201; post created with emoji preserved in topic field
**Test Type**: Unit
**Priority**: Low

---

### TC-007 | Blog Generation API | Topic with only whitespace returns 422
**Precondition**: Valid API request setup
**Steps**:
  1. POST /api/blogs/generate with body `{"topic": "     "}`
  2. Capture response
**Expected Result**: HTTP 422; error message indicates topic cannot be only whitespace
**Test Type**: Unit
**Priority**: High

---

### TC-008 | Blog Generation API | Topic with SQL injection attempt is sanitized
**Precondition**: Valid API request setup
**Steps**:
  1. POST /api/blogs/generate with body `{"topic": "Test'; DROP TABLE posts; --"}`
  2. Create second post to verify table still exists
  3. Verify no data was deleted
**Expected Result**: HTTP 201; post created safely; no SQL executed; topics table intact
**Test Type**: Security
**Priority**: High

---

### TC-009 | Blog Generation API | Topic with XSS script tag is escaped
**Precondition**: Valid API request setup
**Steps**:
  1. POST /api/blogs/generate with body `{"topic": "<script>alert('xss')</script>"}`
  2. GET /api/blogs/{id} to retrieve post
  3. Verify topic in response is escaped or plain text
**Expected Result**: HTTP 201 for POST; GET returns topic as plain text (not executable HTML)
**Test Type**: Security
**Priority**: High

---

### TC-010 | Blog Generation API | Missing AI API key returns 502
**Precondition**: AI API key environment variable is unset
**Steps**:
  1. POST /api/blogs/generate with valid topic
  2. Capture response before timeout
**Expected Result**: HTTP 502; error message "LLM_API_KEY not configured"
**Test Type**: Integration
**Priority**: High

---

### TC-011 | Blog Generation API | AI API timeout after 120 seconds returns 504
**Precondition**: AI API endpoint is configured to timeout
**Steps**:
  1. POST /api/blogs/generate with valid topic
  2. Wait for 120+ seconds
**Expected Result**: HTTP 504; error message "LLM API timeout"
**Test Type**: Integration
**Priority**: High
**Note**: AI-dependent; may mock with delay

---

### TC-012 | Blog Generation API | AI returns malformed JSON is caught
**Precondition**: AI API response is mocked to return invalid JSON
**Steps**:
  1. POST /api/blogs/generate with valid topic
  2. Capture response
**Expected Result**: HTTP 502; error message "Failed to parse LLM response"
**Test Type**: Integration
**Priority**: High

---

### TC-013 | Blog Generation API | Duplicate topic submitted twice creates two separate posts
**Precondition**: First post with topic "SEO Tips" created successfully
**Steps**:
  1. POST /api/blogs/generate with topic "SEO Tips" again
  2. Query GET /api/blogs/ to count posts
**Expected Result**: HTTP 201; two distinct posts created (no uniqueness constraint on topic)
**Test Type**: Unit
**Priority**: Medium

---

### TC-014 | Blog Generation API | Non-English topic (Chinese) is accepted
**Precondition**: Valid API request setup
**Steps**:
  1. POST /api/blogs/generate with body `{"topic": "如何扩展SaaS产品"}`
  2. Capture response
**Expected Result**: HTTP 201; post created with Chinese characters preserved
**Test Type**: Unit
**Priority**: Low

---

### TC-015 | Blog Generation API | Concurrent generation requests both succeed (no race condition)
**Precondition**: Valid API setup; database transaction isolation working
**Steps**:
  1. Spawn two concurrent POST requests to /api/blogs/generate with different topics
  2. Wait for both responses
  3. Verify both posts created with unique IDs
**Expected Result**: HTTP 201 for both; both posts exist; no data corruption
**Test Type**: Integration
**Priority**: High

---

## CATEGORY 2: Blog CRUD Operations (12 test cases)

### TC-016 | Blog CRUD | GET /api/blogs/ returns empty list on fresh database
**Precondition**: Database is empty (no posts)
**Steps**:
  1. GET /api/blogs/
  2. Capture response
**Expected Result**: HTTP 200; response body is `{"data": [], "total": 0, "limit": 10, "skip": 0}`
**Test Type**: Unit
**Priority**: High

---

### TC-017 | Blog CRUD | GET /api/blogs/ returns correct total count
**Precondition**: 5 posts exist in database
**Steps**:
  1. GET /api/blogs/
  2. Verify total field
**Expected Result**: HTTP 200; `total` field equals 5; `data` array length is 5
**Test Type**: Unit
**Priority**: High

---

### TC-018 | Blog CRUD | GET /api/blogs/ pagination with skip=0, limit=5
**Precondition**: 12 posts exist in database
**Steps**:
  1. GET /api/blogs/?skip=0&limit=5
  2. Verify array length and order
**Expected Result**: HTTP 200; `data` array contains exactly 5 items; first item is oldest post
**Test Type**: Unit
**Priority**: High

---

### TC-019 | Blog CRUD | GET /api/blogs/ pagination page 2 with skip=5, limit=5
**Precondition**: 12 posts exist in database
**Steps**:
  1. GET /api/blogs/?skip=5&limit=5
  2. Verify correct items returned
**Expected Result**: HTTP 200; `data` array contains items 6–10; no overlap with page 1
**Test Type**: Unit
**Priority**: High

---

### TC-020 | Blog CRUD | GET /api/blogs/{id} with valid ID returns full post
**Precondition**: Post with ID=1 exists in database
**Steps**:
  1. GET /api/blogs/1
  2. Verify all fields present
**Expected Result**: HTTP 200; response contains `{id, topic, title, content, outline, seo_analysis, status, created_at, updated_at}`
**Test Type**: Unit
**Priority**: High

---

### TC-021 | Blog CRUD | GET /api/blogs/{id} with non-existent ID returns 404
**Precondition**: Database has posts but ID=9999 doesn't exist
**Steps**:
  1. GET /api/blogs/9999
  2. Capture response
**Expected Result**: HTTP 404; error message "Post not found"
**Test Type**: Unit
**Priority**: High

---

### TC-022 | Blog CRUD | GET /api/blogs/{id} with string ID "abc" returns 422
**Precondition**: Valid database setup
**Steps**:
  1. GET /api/blogs/abc
  2. Capture response
**Expected Result**: HTTP 422; error message "id must be an integer"
**Test Type**: Unit
**Priority**: High

---

### TC-023 | Blog CRUD | GET /api/blogs/{id} with negative ID -1 returns 422
**Precondition**: Valid database setup
**Steps**:
  1. GET /api/blogs/-1
  2. Capture response
**Expected Result**: HTTP 422; error message "id must be greater than 0"
**Test Type**: Unit
**Priority**: Medium

---

### TC-024 | Blog CRUD | PUT /api/blogs/{id} updates title only
**Precondition**: Post with ID=1 exists with title "Original Title"
**Steps**:
  1. PUT /api/blogs/1 with body `{"title": "New Title"}`
  2. GET /api/blogs/1 to verify
**Expected Result**: HTTP 200; title field updated to "New Title"; other fields unchanged; updated_at timestamp changes
**Test Type**: Unit
**Priority**: High

---

### TC-025 | Blog CRUD | PUT /api/blogs/{id} updating content triggers SEO re-analysis
**Precondition**: Post exists with seo_score=72; new content is submitted
**Steps**:
  1. PUT /api/blogs/1 with body `{"content": "<new content with 1500 words and proper structure>"}`
  2. GET /api/blogs/1 to check SEO analysis
**Expected Result**: HTTP 200; seo_score may change; SEO analysis is recalculated and updated_at reflects new analysis timestamp
**Test Type**: Integration
**Priority**: High

---

### TC-026 | Blog CRUD | PUT /api/blogs/{id} status updated to "published"
**Precondition**: Post with ID=1 has status="draft"
**Steps**:
  1. PUT /api/blogs/1 with body `{"status": "published"}`
  2. GET /api/blogs/1 to verify
**Expected Result**: HTTP 200; status field is "published"
**Test Type**: Unit
**Priority**: High

---

### TC-027 | Blog CRUD | PUT /api/blogs/{id} with non-existent post returns 404
**Precondition**: No post with ID=9999 exists
**Steps**:
  1. PUT /api/blogs/9999 with body `{"title": "Anything"}`
  2. Capture response
**Expected Result**: HTTP 404; error message "Post not found"
**Test Type**: Unit
**Priority**: High

---

## CATEGORY 3: Delete & Cascade (6 test cases)

### TC-028 | Delete & Cascade | DELETE post removes post row
**Precondition**: Post with ID=1 exists
**Steps**:
  1. DELETE /api/blogs/1
  2. GET /api/blogs/1 to verify deletion
**Expected Result**: HTTP 204 for DELETE; HTTP 404 for GET (post no longer exists)
**Test Type**: Unit
**Priority**: High

---

### TC-029 | Delete & Cascade | DELETE post cascades to outline row
**Precondition**: Post with ID=1 exists; outline with post_id=1 exists
**Steps**:
  1. DELETE /api/blogs/1
  2. Query database or GET /api/outlines/outline_id to check outline status
**Expected Result**: HTTP 204; outline row is deleted from database (cascade)
**Test Type**: Integration
**Priority**: High

---

### TC-030 | Delete & Cascade | DELETE post cascades to seo_analysis row
**Precondition**: Post with ID=1 exists; seo_analysis row with post_id=1 exists
**Steps**:
  1. DELETE /api/blogs/1
  2. Query database or GET /api/seo/1 to check analysis status
**Expected Result**: HTTP 204; seo_analysis row is deleted from database (cascade)
**Test Type**: Integration
**Priority**: High

---

### TC-031 | Delete & Cascade | DELETE non-existent post returns 404
**Precondition**: No post with ID=9999
**Steps**:
  1. DELETE /api/blogs/9999
  2. Capture response
**Expected Result**: HTTP 404; error message "Post not found"; no data modified
**Test Type**: Unit
**Priority**: High

---

### TC-032 | Delete & Cascade | GET deleted post returns 404
**Precondition**: Post ID=1 is deleted via DELETE /api/blogs/1
**Steps**:
  1. GET /api/blogs/1
**Expected Result**: HTTP 404; error message "Post not found"
**Test Type**: Unit
**Priority**: High

---

### TC-033 | Delete & Cascade | GET outline of deleted post returns 404
**Precondition**: Post ID=1 deleted (which cascades outline deletion)
**Steps**:
  1. GET /api/outlines/{outline_id_of_deleted_post}
**Expected Result**: HTTP 404; error message "Outline not found"
**Test Type**: Integration
**Priority**: High

---

## CATEGORY 4: Outline Management (10 test cases)

### TC-034 | Outline Management | GET outline for valid post
**Precondition**: Post with ID=1 exists with outline sections
**Steps**:
  1. GET /api/outlines/{outline_id}
  2. Verify structure of response
**Expected Result**: HTTP 200; response contains `{id, post_id, sections: [{heading, content, level}, ...], created_at, updated_at}`
**Test Type**: Unit
**Priority**: High

---

### TC-035 | Outline Management | GET outline for non-existent post returns 404
**Precondition**: Outline ID doesn't exist in database
**Steps**:
  1. GET /api/outlines/9999
  2. Capture response
**Expected Result**: HTTP 404; error message "Outline not found"
**Test Type**: Unit
**Priority**: High

---

### TC-036 | Outline Management | PUT outline saves edited sections
**Precondition**: Outline with ID=1 exists with 3 sections
**Steps**:
  1. PUT /api/outlines/1 with body `{"sections": [{heading: "Intro", level: 1, content: "..."}, {heading: "Body", level: 2, content: "..."}, {heading: "Conclusion", level: 2, content: "..."}]}`
  2. GET /api/outlines/1 to verify
**Expected Result**: HTTP 200; sections saved exactly as provided; updated_at changes
**Test Type**: Integration
**Priority**: High

---

### TC-037 | Outline Management | PUT outline with empty sections array
**Precondition**: Outline with ID=1 exists
**Steps**:
  1. PUT /api/outlines/1 with body `{"sections": []}`
  2. GET /api/outlines/1 to verify
**Expected Result**: HTTP 200; sections array is empty; updated_at changes; status may revert to "draft"
**Test Type**: Unit
**Priority**: Medium

---

### TC-038 | Outline Management | PUT outline resets post status to "draft"
**Precondition**: Post with ID=1 has status="published"; outline is edited
**Steps**:
  1. PUT /api/outlines/{outline_id} with new sections
  2. GET /api/blogs/1 to check post status
**Expected Result**: HTTP 200; post status reverts to "draft" (outline edit invalidates published state)
**Test Type**: Integration
**Priority**: High

---

### TC-039 | Outline Management | PUT outline with 20+ sections (large payload)
**Precondition**: Valid outline setup; 20 sections prepared
**Steps**:
  1. PUT /api/outlines/{id} with 20 sections
  2. Verify all saved
**Expected Result**: HTTP 200; all 20 sections saved; no truncation or data loss
**Test Type**: Unit
**Priority**: Medium

---

### TC-040 | Outline Management | PUT outline missing required "heading" field returns 422
**Precondition**: Outline with ID=1 exists
**Steps**:
  1. PUT /api/outlines/1 with body `{"sections": [{level: 1}]}` (missing heading)
  2. Capture response
**Expected Result**: HTTP 422; error message includes "heading field required"
**Test Type**: Unit
**Priority**: High

---

### TC-041 | Outline Management | PUT outline with invalid level (level=5) returns 422
**Precondition**: Valid outline setup
**Steps**:
  1. PUT /api/outlines/{id} with body containing `{level: 5}`
  2. Capture response
**Expected Result**: HTTP 422; error message "level must be between 1 and 3"
**Test Type**: Unit
**Priority**: High

---

### TC-042 | Outline Management | POST regenerate outline replaces existing sections
**Precondition**: Outline with ID=1 has 3 sections; AI API is functional
**Steps**:
  1. POST /api/outlines/1/regenerate
  2. GET /api/outlines/1 to verify new sections
**Expected Result**: HTTP 200; sections are new and different from original; section count may change
**Test Type**: Integration
**Priority**: High
**Note**: AI-dependent; mock response

---

### TC-043 | Outline Management | POST regenerate outline for non-existent post returns 404
**Precondition**: Outline ID doesn't exist
**Steps**:
  1. POST /api/outlines/9999/regenerate
  2. Capture response
**Expected Result**: HTTP 404; error message "Outline not found"
**Test Type**: Unit
**Priority**: High

---

## CATEGORY 5: SEO Analysis (12 test cases)

### TC-044 | SEO Analysis | GET SEO analysis for valid post
**Precondition**: Post with ID=1 exists; SEO analysis has been run
**Steps**:
  1. GET /api/seo/1
  2. Verify all SEO fields present
**Expected Result**: HTTP 200; response contains `{id, post_id, keyword_density, heading_hierarchy, readability_score, title_variations, meta_description, seo_score, created_at}`
**Test Type**: Unit
**Priority**: High

---

### TC-045 | SEO Analysis | GET SEO analysis for post with no analysis yet returns 404
**Precondition**: Post with ID=2 exists but no SEO analysis run
**Steps**:
  1. GET /api/seo/2
  2. Capture response
**Expected Result**: HTTP 404; error message "No SEO analysis found for this post"
**Test Type**: Unit
**Priority**: High

---

### TC-046 | SEO Analysis | POST re-analyse updates keyword_density field
**Precondition**: Post with ID=1 has content and existing analysis with keyword_density
**Steps**:
  1. POST /api/seo/1/analyse
  2. GET /api/seo/1 to compare keyword_density
**Expected Result**: HTTP 200; keyword_density is recalculated; created_at of analysis is updated
**Test Type**: Integration
**Priority**: High

---

### TC-047 | SEO Analysis | POST re-analyse updates heading_hierarchy field
**Precondition**: Post with content and existing analysis
**Steps**:
  1. Modify post content to include multiple H1 tags (invalid structure)
  2. POST /api/seo/1/analyse
  3. GET /api/seo/1 and check heading_hierarchy.issues
**Expected Result**: HTTP 200; heading_hierarchy.issues contains warning about multiple H1s
**Test Type**: Integration
**Priority**: High

---

### TC-048 | SEO Analysis | POST re-analyse on post with empty content returns 400
**Precondition**: Post with ID=3 has content="" (empty)
**Steps**:
  1. POST /api/seo/3/analyse
  2. Capture response
**Expected Result**: HTTP 400; error message "Cannot analyse empty content"
**Test Type**: Unit
**Priority**: High

---

### TC-049 | SEO Analysis | SEO score equals 100 when all criteria met
**Precondition**: Post with perfect SEO: exactly 1 H1, 2+ H2s, 800+ words, Flesch 30–70, keyword density <3%, meta description present, no heading issues
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. GET /api/seo/{id} and check seo_score
**Expected Result**: HTTP 200; seo_score=100 (or 100 when all criteria weights sum to 100)
**Test Type**: Integration
**Priority**: High

---

### TC-050 | SEO Analysis | SEO score equals 0 when all criteria fail
**Precondition**: Post with: no H1, <2 H2s, <500 words, Flesch <30 or >70, keyword density >3%, no meta description, heading issues
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. GET /api/seo/{id} and check seo_score
**Expected Result**: HTTP 200; seo_score approaches 0 (or 0 if all criteria are worth equal points)
**Test Type**: Integration
**Priority**: High

---

### TC-051 | SEO Analysis | Keyword density excludes stop words
**Precondition**: Content with keywords: "machine learning AI", filled with stop words "the", "and", "is"
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. Verify keyword_density for "the" and "is" are low or zero
**Expected Result**: HTTP 200; keyword_density does not count stop words; "machine learning" counts correctly
**Test Type**: Integration
**Priority**: Medium

---

### TC-052 | SEO Analysis | Keyword density caps at top 15 keywords
**Precondition**: Content with 30 unique keywords
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. Count entries in keyword_density object
**Expected Result**: HTTP 200; keyword_density contains maximum 15 keys
**Test Type**: Unit
**Priority**: Medium

---

### TC-053 | SEO Analysis | H1 missing triggers warning in issues list
**Precondition**: Content with no H1 tag, but has H2s
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. GET /api/seo/{id} and check heading_hierarchy.issues
**Expected Result**: HTTP 200; heading_hierarchy.issues array includes "Missing H1 heading"
**Test Type**: Integration
**Priority**: High

---

### TC-054 | SEO Analysis | Multiple H1 tags trigger warning in issues list
**Precondition**: Content with 3 H1 tags
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. GET /api/seo/{id} and check heading_hierarchy.issues
**Expected Result**: HTTP 200; heading_hierarchy.issues includes "Too many H1 headings (found 3, expected 1)"
**Test Type**: Integration
**Priority**: High

---

### TC-055 | SEO Analysis | POST analyse-text analyzes arbitrary text without post ID
**Precondition**: Valid API request setup
**Steps**:
  1. POST /api/seo/analyse-text with body `{"text": "<full blog content>", "keywords": ["SEO", "blog"]}`
  2. Capture response
**Expected Result**: HTTP 200; response contains SEO analysis results for provided text (no post ID required)
**Test Type**: Unit
**Priority**: Medium

---

## CATEGORY 6: Readability Scoring (8 test cases)

### TC-056 | Readability Scoring | Simple short sentences score above 70
**Precondition**: Content with short simple sentences: "The cat sat. It was black. I like cats."
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. Check readability_score
**Expected Result**: HTTP 200; readability_score > 70
**Test Type**: Unit
**Priority**: High

---

### TC-057 | Readability Scoring | Complex academic text scores below 50
**Precondition**: Content with complex academic language: "The dichotomy of epistemological frameworks necessitates comprehensive investigative methodologies..."
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. Check readability_score
**Expected Result**: HTTP 200; readability_score < 50
**Test Type**: Unit
**Priority**: High

---

### TC-058 | Readability Scoring | Empty content returns score of 0
**Precondition**: Content is empty string ""
**Steps**:
  1. POST /api/seo/{id}/analyse with empty content
  2. Capture response or check readability_score
**Expected Result**: HTTP 200 or 400; readability_score=0 (or error returned)
**Test Type**: Unit
**Priority**: High

---

### TC-059 | Readability Scoring | Score is always between 0 and 100
**Precondition**: Any valid content
**Steps**:
  1. POST /api/seo/{id}/analyse with various content types
  2. Verify readability_score range
**Expected Result**: HTTP 200; readability_score is always >= 0 and <= 100
**Test Type**: Unit
**Priority**: High

---

### TC-060 | Readability Scoring | Correct label for score 95 is "Very Easy"
**Precondition**: Content that generates readability_score=95
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. GET /api/seo/{id} and check readability_label
**Expected Result**: HTTP 200; readability_label="Very Easy"
**Test Type**: Unit
**Priority**: Medium

---

### TC-061 | Readability Scoring | Correct label for score 65 is "Standard"
**Precondition**: Content that generates readability_score=65
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. GET /api/seo/{id} and check readability_label
**Expected Result**: HTTP 200; readability_label="Standard"
**Test Type**: Unit
**Priority**: Medium

---

### TC-062 | Readability Scoring | Correct label for score 25 is "Very Confusing"
**Precondition**: Content that generates readability_score=25
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. GET /api/seo/{id} and check readability_label
**Expected Result**: HTTP 200; readability_label="Very Confusing"
**Test Type**: Unit
**Priority**: Medium

---

### TC-063 | Readability Scoring | Gunning Fog Index is always positive
**Precondition**: Any valid content
**Steps**:
  1. POST /api/seo/{id}/analyse
  2. Check Gunning Fog field in response
**Expected Result**: HTTP 200; Gunning Fog value > 0 (always positive number)
**Test Type**: Unit
**Priority**: Medium

---

## CATEGORY 7: Title & Meta Generation (6 test cases)

### TC-064 | Title & Meta Generation | Returns exactly 5 title variations
**Precondition**: Post with content; SEO analysis run
**Steps**:
  1. GET /api/seo/{id} and check title_variations
**Expected Result**: HTTP 200; title_variations is array of exactly 5 elements
**Test Type**: Unit
**Priority**: High

---

### TC-065 | Title & Meta Generation | All 5 titles are unique (no duplicates)
**Precondition**: Post with title_variations already generated
**Steps**:
  1. GET /api/seo/{id} and check title_variations
  2. Compare each title to others
**Expected Result**: HTTP 200; all 5 titles are different (no duplicates)
**Test Type**: Unit
**Priority**: High

---

### TC-066 | Title & Meta Generation | Meta description is 160 chars or less
**Precondition**: Post with SEO analysis
**Steps**:
  1. GET /api/seo/{id} and check meta_description
  2. Count characters
**Expected Result**: HTTP 200; meta_description.length <= 160
**Test Type**: Unit
**Priority**: High

---

### TC-067 | Title & Meta Generation | Meta description contains focus keyword
**Precondition**: Post with focus_keyword="SEO tips"; SEO analysis run
**Steps**:
  1. GET /api/seo/{id} and check meta_description
**Expected Result**: HTTP 200; meta_description.toLowerCase() contains focus_keyword.toLowerCase()
**Test Type**: Unit
**Priority**: High

---

### TC-068 | Title & Meta Generation | Title variations are all strings (not null/empty)
**Precondition**: Post with title_variations generated
**Steps**:
  1. GET /api/seo/{id} and check each title in title_variations array
**Expected Result**: HTTP 200; all titles are non-empty strings (not null, not "")
**Test Type**: Unit
**Priority**: High

---

### TC-069 | Title & Meta Generation | Chosen title can be updated via PUT
**Precondition**: Post with ID=1 and title_variations available
**Steps**:
  1. PUT /api/blogs/1 with body `{"title": "New Title"}`
  2. GET /api/blogs/1 to verify
**Expected Result**: HTTP 200; title field is updated to "New Title"; SEO analysis may flag title length
**Test Type**: Unit
**Priority**: Medium

---

## CATEGORY 8: Export Functionality (10 test cases)

### TC-070 | Export Functionality | GET /markdown returns 200 with correct Content-Type
**Precondition**: Post with ID=1 exists and has content
**Steps**:
  1. GET /api/export/1/markdown
  2. Check HTTP status and Content-Type header
**Expected Result**: HTTP 200; Content-Type header is "text/markdown" or "text/plain"
**Test Type**: Unit
**Priority**: High

---

### TC-071 | Export Functionality | GET /markdown filename is blog-post-{id}.md
**Precondition**: Post with ID=1 exists
**Steps**:
  1. GET /api/export/1/markdown
  2. Check Content-Disposition header
**Expected Result**: HTTP 200; Content-Disposition header includes filename="blog-post-1.md"
**Test Type**: Unit
**Priority**: High

---

### TC-072 | Export Functionality | Markdown export contains YAML front-matter block
**Precondition**: Post with ID=1 exists with metadata
**Steps**:
  1. GET /api/export/1/markdown
  2. Parse response body for YAML block
**Expected Result**: HTTP 200; response body starts with `---` followed by YAML, ending with `---`
**Test Type**: Unit
**Priority**: High

---

### TC-073 | Export Functionality | Markdown front-matter has title, description, slug, date
**Precondition**: Post with metadata exists
**Steps**:
  1. GET /api/export/1/markdown
  2. Parse YAML front-matter
**Expected Result**: HTTP 200; YAML contains keys: title, description, slug, date (all present)
**Test Type**: Unit
**Priority**: High

---

### TC-074 | Export Functionality | Markdown body contains actual blog content after front-matter
**Precondition**: Post with content "## Section 1\nThis is content" exists
**Steps**:
  1. GET /api/export/1/markdown
  2. Parse body after YAML block
**Expected Result**: HTTP 200; response body after `---` contains "## Section 1" and "This is content"
**Test Type**: Unit
**Priority**: High

---

### TC-075 | Export Functionality | GET /html returns 200 with text/html Content-Type
**Precondition**: Post with ID=1 exists
**Steps**:
  1. GET /api/export/1/html
  2. Check HTTP status and Content-Type header
**Expected Result**: HTTP 200; Content-Type header is "text/html"
**Test Type**: Unit
**Priority**: High

---

### TC-076 | Export Functionality | HTML export contains <!DOCTYPE html>
**Precondition**: Post with ID=1 exists
**Steps**:
  1. GET /api/export/1/html
  2. Check response body starts with doctype
**Expected Result**: HTTP 200; response body starts with `<!DOCTYPE html>` (case-insensitive)
**Test Type**: Unit
**Priority**: High

---

### TC-077 | Export Functionality | HTML export contains meta description tag
**Precondition**: Post with meta_description="Blog description" exists
**Steps**:
  1. GET /api/export/1/html
  2. Search for meta description tag
**Expected Result**: HTTP 200; response contains `<meta name="description" content="Blog description">`
**Test Type**: Unit
**Priority**: High

---

### TC-078 | Export Functionality | HTML export contains Open Graph meta tags
**Precondition**: Post with title and content exists
**Steps**:
  1. GET /api/export/1/html
  2. Search for og: meta tags
**Expected Result**: HTTP 200; response contains `<meta property="og:title">`, `<meta property="og:description">`, and `<meta property="og:type" content="article">`
**Test Type**: Unit
**Priority**: High

---

### TC-079 | Export Functionality | Export of non-existent post returns 404
**Precondition**: Post ID=9999 doesn't exist
**Steps**:
  1. GET /api/export/9999/markdown
  2. GET /api/export/9999/html
**Expected Result**: HTTP 404 for both; error message "Post not found"
**Test Type**: Unit
**Priority**: High

---

## CATEGORY 9: Regenerate Blog Content (5 test cases)

### TC-080 | Regenerate Blog Content | POST regenerate returns new content
**Precondition**: Post with ID=1 has outline; AI API functional
**Steps**:
  1. Record original content value
  2. POST /api/blogs/1/regenerate
  3. GET /api/blogs/1 and check content
**Expected Result**: HTTP 200; content field is non-empty and different from original
**Test Type**: Integration
**Priority**: High
**Note**: AI-dependent; mock response

---

### TC-081 | Regenerate Blog Content | Regenerated content differs from original
**Precondition**: Post with content regenerated twice
**Steps**:
  1. Record content after 1st regeneration
  2. POST /api/blogs/{id}/regenerate again (temp=0.8 for variation)
  3. Compare new content with previous
**Expected Result**: HTTP 200; new content is different (due to temperature variation)
**Test Type**: Integration
**Priority**: High

---

### TC-082 | Regenerate Blog Content | Regenerate uses updated outline sections
**Precondition**: Post with outline; outline is edited to have different section headings
**Steps**:
  1. PUT /api/outlines/{id} with new sections
  2. POST /api/blogs/{id}/regenerate
  3. Verify content includes new section headings
**Expected Result**: HTTP 200; generated content follows updated outline structure
**Test Type**: Integration
**Priority**: High

---

### TC-083 | Regenerate Blog Content | Regenerate on post with no outline returns 400
**Precondition**: Post with ID=1 has no outline (outline deleted or never created)
**Steps**:
  1. POST /api/blogs/1/regenerate
  2. Capture response
**Expected Result**: HTTP 400; error message "No outline found for this post"
**Test Type**: Unit
**Priority**: High

---

### TC-084 | Regenerate Blog Content | Regenerate on non-existent post returns 404
**Precondition**: Post ID=9999 doesn't exist
**Steps**:
  1. POST /api/blogs/9999/regenerate
  2. Capture response
**Expected Result**: HTTP 404; error message "Post not found"
**Test Type**: Unit
**Priority**: High

---

## CATEGORY 10: Database & Models (8 test cases)

### TC-085 | Database & Models | Post created_at timestamp set automatically
**Precondition**: Post created via POST /api/blogs/generate
**Steps**:
  1. GET /api/blogs/{id} immediately after creation
  2. Check created_at field
**Expected Result**: HTTP 200; created_at is a valid ISO 8601 timestamp; matches current time (within 2 seconds)
**Test Type**: Integration
**Priority**: High

---

### TC-086 | Database & Models | Post updated_at changes on PUT request
**Precondition**: Post created 10 seconds ago with known updated_at; now edit via PUT
**Steps**:
  1. Record updated_at value
  2. Wait 1 second
  3. PUT /api/blogs/{id} with new title
  4. GET /api/blogs/{id} and check updated_at again
**Expected Result**: HTTP 200; new updated_at is later than old value
**Test Type**: Integration
**Priority**: High

---

### TC-087 | Database & Models | Outline sections stored and retrieved as valid JSON
**Precondition**: Outline with sections array created
**Steps**:
  1. PUT /api/outlines/{id} with complex nested JSON sections
  2. GET /api/outlines/{id} to retrieve
**Expected Result**: HTTP 200; sections field is valid JSON; structure matches input exactly
**Test Type**: Integration
**Priority**: High

---

### TC-088 | Database & Models | SEO keyword_density stored and retrieved as valid JSON
**Precondition**: SEO analysis run on post
**Steps**:
  1. GET /api/seo/{id}
  2. Check keyword_density field
**Expected Result**: HTTP 200; keyword_density is valid JSON object (not string); can iterate keys
**Test Type**: Unit
**Priority**: High

---

### TC-089 | Database & Models | SEO title_variations stored as JSON array of 5 strings
**Precondition**: SEO analysis generated title variations
**Steps**:
  1. GET /api/seo/{id}
  2. Check title_variations field
**Expected Result**: HTTP 200; title_variations is JSON array; length=5; all elements are strings
**Test Type**: Unit
**Priority**: High

---

### TC-090 | Database & Models | post_status ENUM rejects invalid value "archived"
**Precondition**: Valid Post object setup
**Steps**:
  1. PUT /api/blogs/{id} with body `{"status": "archived"}`
  2. Capture response
**Expected Result**: HTTP 422; error message "status must be one of: draft, generated, published"
**Test Type**: Unit
**Priority**: High

---

### TC-091 | Database & Models | Two posts can have same topic (no unique constraint)
**Precondition**: Post 1 created with topic "SEO"
**Steps**:
  1. POST /api/blogs/generate with topic "SEO" again
  2. Verify both posts exist
**Expected Result**: HTTP 201; two posts created; both have topic="SEO"; no duplicate constraint error
**Test Type**: Unit
**Priority**: Medium

---

### TC-092 | Database & Models | SEO analysis has unique constraint on post_id
**Precondition**: Post with ID=1 has one SEO analysis
**Steps**:
  1. Attempt to insert second seo_analyses row with same post_id via database
  2. Capture error
**Expected Result**: Database constraint error or HTTP 422; cannot create duplicate; one seo_analysis per post
**Test Type**: Integration
**Priority**: High

---

## CATEGORY 11: Frontend UI (8 test cases)

### TC-093 | Frontend UI | TopicInput page renders textarea and Generate button
**Precondition**: Frontend loaded at http://localhost:5173
**Steps**:
  1. Navigate to home page
  2. Look for textarea element
  3. Look for "Generate" button
**Expected Result**: Textarea is visible and focused-able; "Generate" button is visible and clickable
**Test Type**: UI
**Priority**: High

---

### TC-094 | Frontend UI | Generate button is disabled when textarea is empty
**Precondition**: TopicInput page loaded; textarea is empty
**Steps**:
  1. Inspect "Generate" button state
**Expected Result**: Button has `disabled` attribute or CSS class; not clickable
**Test Type**: UI
**Priority**: High

---

### TC-095 | Frontend UI | Generate button is disabled while loading
**Precondition**: TopicInput page with topic entered; click Generate
**Steps**:
  1. Click Generate button
  2. Immediately check button state before response arrives
**Expected Result**: Button is disabled during fetch; may show "Generating..." text
**Test Type**: UI
**Priority**: High

---

### TC-096 | Frontend UI | Loading spinner appears during generation
**Precondition**: Clicked Generate button; API call in progress
**Steps**:
  1. Wait for 1–5 seconds during API call
  2. Look for spinner/loader element
**Expected Result**: Spinner element is visible; animates; shows "Generating blog outline..."
**Test Type**: UI
**Priority**: High

---

### TC-097 | Frontend UI | OutlineEditor displays all sections from API
**Precondition**: After blog generation completes; EditorPage loaded
**Steps**:
  1. Navigate to editor page (or automatically redirected)
  2. Check OutlinePanel (left side)
**Expected Result**: All outline sections are displayed; each as draggable item; heading text visible
**Test Type**: UI
**Priority**: High

---

### TC-098 | Frontend UI | Section heading is editable inline
**Precondition**: EditorPage loaded with outline visible
**Steps**:
  1. Double-click on a section heading
  2. Type new heading text
  3. Press Enter or click outside
**Expected Result**: Heading becomes editable; new text is saved; changes reflected in UI
**Test Type**: UI
**Priority**: High

---

### TC-099 | Frontend UI | SEO Dashboard shows score ring with correct number
**Precondition**: EditorPage loaded; SEO analysis displayed on right panel
**Steps**:
  1. Look for circular SEO score ring (SVG or canvas)
  2. Check number displayed in center
**Expected Result**: Ring is visible; number (0–100) is displayed in center; ring fill corresponds to percentage
**Test Type**: UI
**Priority**: High

---

### TC-100 | Frontend UI | History page shows all posts with status badges
**Precondition**: Frontend loaded; navigate to History page
**Steps**:
  1. Navigate to /history or History link in nav
  2. Check post list/table
**Expected Result**: Table/list displays all posts; each row has status badge (Draft, Published, Generated); badges have different colors
**Test Type**: UI
**Priority**: High

---

## SUMMARY

**Total Test Cases**: 100
- **Category 1** (Blog Generation API): 15 cases
- **Category 2** (Blog CRUD): 12 cases
- **Category 3** (Delete & Cascade): 6 cases
- **Category 4** (Outline Management): 10 cases
- **Category 5** (SEO Analysis): 12 cases
- **Category 6** (Readability Scoring): 8 cases
- **Category 7** (Title & Meta): 6 cases
- **Category 8** (Export): 10 cases
- **Category 9** (Regenerate): 5 cases
- **Category 10** (Database): 8 cases
- **Category 11** (Frontend UI): 8 cases

**Coverage**:
- ✅ Happy path and edge cases
- ✅ HTTP status codes (200, 201, 204, 400, 404, 422, 502, 504)
- ✅ Security tests (SQL injection, XSS, oversized payloads)
- ✅ Database constraints and cascading deletes
- ✅ API response validation
- ✅ Frontend UI interaction
- ✅ AI API integration (mocked)
- ✅ Error handling and validation

**Execution Recommendations**:
- High Priority: Run before every release
- Medium Priority: Run nightly or weekly
- Low Priority: Run on-demand or quarterly
- AI-dependent tests: Mock LLM responses in CI/CD pipeline
- Database-dependent tests: Use transactional rollback for isolation
